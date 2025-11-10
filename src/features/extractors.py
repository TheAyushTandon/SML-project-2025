import pandas as pd
import numpy as np
import math
import string
import os

def password_entropy(password):
    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(c in string.punctuation for c in password): pool += len(string.punctuation)
    if pool == 0: return 0
    return len(password) * math.log2(pool)

def extract_features(password):
    length = len(password)
    upper = sum(1 for c in password if c.isupper())
    lower = sum(1 for c in password if c.islower())
    digits = sum(1 for c in password if c.isdigit())
    special = sum(1 for c in password if c in string.punctuation)
    diversity = len(set(password)) / length if length > 0 else 0
    entropy = password_entropy(password)
    sequences = ['123', 'abc', 'qwe', 'xyz', 'password']
    seq_score = sum(seq in password.lower() for seq in sequences)

    return {
        "length": length,
        "upper": upper,
        "lower": lower,
        "digits": digits,
        "special": special,
        "diversity": diversity,
        "entropy": entropy,
        "sequence_score": seq_score,
        "password": password
    }

def load_passwords_from_dataset(dataset_dir):
    passwords = []
    labels = []
    for label in ["weak", "medium", "strong"]:
        path = os.path.join(dataset_dir, label + ".txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    pw = line.strip()
                    if len(pw) > 0:
                        passwords.append(pw)
                        labels.append(label)
    return passwords, labels

def generate_features(dataset_dir="datasets/", output_path="data/password_features.csv"):
    passwords, labels = load_passwords_from_dataset(dataset_dir)
    data = [extract_features(pw) for pw in passwords]
    df = pd.DataFrame(data)
    df["label"] = labels
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Features extracted from {len(df)} passwords and saved to {output_path}")
