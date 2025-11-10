# src/unsupervised/detector.py
import json, os
import numpy as np
import torch
import torch.nn.functional as F
import joblib
from pathlib import Path
import math
import re

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "models" / "unsupervised"
CHAR2IDX_PATH = OUT_DIR / "char2idx.json"
AE_PATH = OUT_DIR / "autoencoder.pt"
IF_PATH = OUT_DIR / "isoforest.pkl"
META_PATH = OUT_DIR / "unsup_meta.json"
MAX_LEN = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# load char2idx
with open(CHAR2IDX_PATH, "r", encoding="utf-8") as f:
    CHAR2IDX = json.load(f)
PAD = CHAR2IDX.get("<pad>", 0)
UNK = CHAR2IDX.get("<unk>", 1)
VOCAB_SIZE = max(CHAR2IDX.values()) + 1

# Model (must match training)
import torch.nn as nn
class SeqAutoencoder(nn.Module):
    def __init__(self, vocab_size, emb_dim=64, hidden_dim=128, pad_idx=0):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_idx)
        self.encoder = nn.GRU(emb_dim, hidden_dim, batch_first=True)
        self.decoder = nn.GRU(emb_dim, hidden_dim, batch_first=True)
        self.output = nn.Linear(hidden_dim, vocab_size)
    def forward(self, x):
        emb = self.emb(x)
        _, h = self.encoder(emb)
        dec_in = emb
        dec_out, _ = self.decoder(dec_in, h)
        logits = self.output(dec_out)
        return logits

AE = SeqAutoencoder(VOCAB_SIZE, emb_dim=64, hidden_dim=128, pad_idx=PAD)
AE.load_state_dict(torch.load(AE_PATH, map_location="cpu"))
AE.to(DEVICE).eval()

IF = joblib.load(IF_PATH)

# helper functions
def encode_pwd(pw, max_len=MAX_LEN):
    idxs = [CHAR2IDX.get(c, UNK) for c in pw[:max_len]]
    if len(idxs) < max_len:
        idxs += [PAD] * (max_len - len(idxs))
    return np.array(idxs, dtype=np.int64)

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
        for count in ctr.values():
            p = count / l
            ent -= p * math.log2(p)
    return np.array([l, digits, upper, lower, symbols, uniq, ent], dtype=np.float32)

def reconstruction_error(pw_seq):
    # pw_seq: numpy array shape [L]
    x = torch.tensor(pw_seq[None,:], dtype=torch.long, device=DEVICE)
    with torch.no_grad():
        logits = AE(x)  # [1,L,V]
        probs = F.log_softmax(logits, dim=-1)  # log-probs
        # negative log-likelihood of true tokens:
        token_ll = -probs[0, torch.arange(probs.size(1)), x[0]]
        # ignore pads
        pad_mask = (x[0] == PAD)
        token_ll = token_ll[~pad_mask]
        if token_ll.numel()==0:
            return float("inf")
        return float(token_ll.mean().cpu().item())  # mean NLL

def score_password(password):
    # returns dict with anomaly / risk metrics
    seq = encode_pwd(password)
    rec_err = reconstruction_error(seq)  # lower = easier to reconstruct (more like training)
    struct = extract_struct_features(password).reshape(1,-1)
    if_score = IF.score_samples(struct)[0]  # higher = normal (positive), lower negative -> anomalous
    # Normalize and combine into 0..1 anomaly score:
    # map rec_err -> 0..1 (we invert: large rec_err -> anomaly)
    # we need heuristics to scale: use plausible range
    rec_clamped = min(max(rec_err, 0.0), 10.0)  # clamp
    rec_norm = (rec_clamped / 10.0)  # 0..1

    # isolation forest: score_samples gives higher for normal; convert to anomaly in 0..1
    # typical IF outputs in [-1,1], but score_samples are log-odds-like; use percentile-style transform
    if_norm = 1.0 - (1.0 / (1.0 + np.exp(if_score)))  # sigmoid invert (rough)

    # combine: weighted sum (tunable)
    # rec_norm: higher => more anomalous; if_norm higher => more anomalous
    anomaly_raw = 0.6 * rec_norm + 0.4 * if_norm
    anomaly = float(np.clip(anomaly_raw, 0.0, 1.0))

    return {
        "reconstruction_error": rec_err,
        "reconstruction_norm": rec_norm,
        "isoforest_raw": float(if_score),
        "isoforest_norm": float(if_norm),
        "anomaly_score": anomaly
    }

if __name__ == "__main__":
    for pw in ["123456","password","qwerty123","helloWORLD","S0m3Rand0m#Chars!","fbeiabig83791brob*%^#@@()"]:
        print(pw, "->", score_password(pw))
