# src/unsupervised/train_autoencoder.py
import os
import json
import random
from pathlib import Path
from tqdm import tqdm

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from sklearn.ensemble import IsolationForest
import joblib

# -------------------------
# Config / paths
# -------------------------
ROOT = Path(__file__).resolve().parents[2]   # points to repo root
DATA_PATH = ROOT / "data" / "xato" / "10-million-passwords.txt"
OUT_DIR = ROOT / "models" / "unsupervised"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHAR2IDX_PATH = OUT_DIR / "char2idx.json"
AE_PATH = OUT_DIR / "autoencoder.pt"
IF_PATH = OUT_DIR / "isoforest.pkl"
META_PATH = OUT_DIR / "unsup_meta.json"

MAX_LEN = 32
EMB_DIM = 64
HIDDEN_DIM = 128
BATCH_SIZE = 1024
EPOCHS = 6
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# -------------------------
# Simple char tokenizer
# -------------------------
def build_char_vocab(passwords):
    chars = sorted(list({c for p in passwords for c in p}))
    # reserve 0 for pad, 1 for unk
    char2idx = {ch: i+2 for i, ch in enumerate(chars)}
    char2idx["<pad>"] = 0
    char2idx["<unk>"] = 1
    return char2idx

def encode_pwd(pwd, char2idx, max_len=MAX_LEN):
    idxs = [char2idx.get(c, char2idx["<unk>"]) for c in pwd[:max_len]]
    if len(idxs) < max_len:
        idxs += [char2idx["<pad>"]] * (max_len - len(idxs))
    return idxs

# -------------------------
# PyTorch dataset
# -------------------------
class PwDataset(Dataset):
    def __init__(self, pw_list, char2idx):
        self.pw_list = pw_list
        self.char2idx = char2idx

    def __len__(self):
        return len(self.pw_list)

    def __getitem__(self, idx):
        seq = encode_pwd(self.pw_list[idx], self.char2idx)
        return torch.tensor(seq, dtype=torch.long)

# -------------------------
# Autoencoder model (char-level)
# -------------------------
class SeqAutoencoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=EMB_DIM, hidden_dim=HIDDEN_DIM, pad_idx=0):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_idx)
        self.encoder = nn.GRU(emb_dim, hidden_dim, batch_first=True)
        self.decoder = nn.GRU(emb_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        # x: [B, L]
        emb = self.emb(x)  # [B, L, E]
        _, h = self.encoder(emb)  # [1, B, H]
        # Start decoding with last hidden and use teacher forcing
        dec_in = emb  # teacher forcing: feed embeddings of input shifted, simpler: feed emb
        dec_out, _ = self.decoder(dec_in, h)
        logits = self.output(dec_out)  # [B, L, V]
        return logits

# -------------------------
# Feature extractor for IsolationForest (simple structural features)
# -------------------------
import re
def extract_struct_features(pw):
    pw = str(pw)
    l = len(pw)
    digits = sum(c.isdigit() for c in pw)
    upper = sum(c.isupper() for c in pw)
    lower = sum(c.islower() for c in pw)
    symbols = len(re.findall(r'[^a-zA-Z0-9]', pw))
    uniq = len(set(pw))
    ent = 0.0
    if l>0:
        from collections import Counter
        ctr = Counter(pw)
        import math
        for count in ctr.values():
            p = count / l
            ent -= p * math.log2(p)
    return [l, digits, upper, lower, symbols, uniq, ent]

# -------------------------
# Training loop
# -------------------------
def train():
    print("[INFO] Loading sample passwords (may be large) ...")
    # We sample to keep GPU/CPU training feasible. Use more for production.
    passwords = []
    with open(DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pw = line.strip()
            if pw:
                passwords.append(pw)
    print(f"[INFO] Loaded {len(passwords):,} passwords. Sampling for training...")

    # Shuffle and sample (adjust sample_size as you like)
    random.shuffle(passwords)
    sample_size = min(500_000, len(passwords))  # safe default
    passwords = passwords[:sample_size]
    print(f"[INFO] Using {len(passwords):,} passwords for training.")

    char2idx = build_char_vocab(passwords)
    vocab_size = max(char2idx.values()) + 1
    # Save char2idx
    with open(CHAR2IDX_PATH, "w", encoding="utf-8") as f:
        json.dump(char2idx, f, ensure_ascii=False)

    # DataLoader
    ds = PwDataset(passwords, char2idx)
    dl = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=4, pin_memory=True)

    # Model
    model = SeqAutoencoder(vocab_size, emb_dim=EMB_DIM, hidden_dim=HIDDEN_DIM, pad_idx=char2idx["<pad>"])
    model.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss(ignore_index=char2idx["<pad>"])

    print("[INFO] Training autoencoder on sampled passwords...")
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for batch in tqdm(dl, desc=f"Epoch {epoch+1}/{EPOCHS}"):
            batch = batch.to(DEVICE)  # [B,L]
            logits = model(batch)     # [B,L,V]
            # compute loss: flatten
            loss = criterion(logits.view(-1, logits.size(-1)), batch.view(-1))
            opt.zero_grad(); loss.backward(); opt.step()
            total_loss += float(loss.item())
        print(f"[INFO] Epoch {epoch+1} loss: {total_loss/len(dl):.4f}")

    # Save AE
    torch.save(model.state_dict(), AE_PATH)
    print(f"[✅] Autoencoder saved -> {AE_PATH}")

    # -------------------------
    # Build IsolationForest on structural features
    # -------------------------
    print("[INFO] Extracting structural features for IsolationForest...")
    feats = np.array([extract_struct_features(p) for p in tqdm(passwords)])
    print("[INFO] Fitting IsolationForest...")
    if_model = IsolationForest(n_estimators=200, max_samples=100000, contamination=0.01, random_state=42, n_jobs=-1)
    if_model.fit(feats)
    joblib.dump(if_model, IF_PATH)
    print(f"[✅] IsolationForest saved -> {IF_PATH}")

    # Save metadata
    meta = {"char2idx": str(CHAR2IDX_PATH.name), "max_len": MAX_LEN, "vocab_size": vocab_size}
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f)
    print(f"[✅] Meta saved -> {META_PATH}")

if __name__ == "__main__":
    train()
