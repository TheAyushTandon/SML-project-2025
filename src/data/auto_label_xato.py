import pandas as pd
import numpy as np
import re
import os
from tqdm import tqdm
from collections import Counter

# Define file paths
DATA_PATH = os.path.join("data", "xato", "10-million-passwords.txt")
OUTPUT_PATH = os.path.join("data", "labeled", "xato_labeled.csv")

# Load the raw passwords
print("[INFO] Loading xato.net password list...")
with open(DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
    passwords = [line.strip() for line in f if line.strip()]

print(f"[INFO] Loaded {len(passwords):,} passwords.")


# Helper function to label password strength
def rule_based_strength(password):
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)

    # Compute entropy
    unique_chars = len(set(password))
    entropy = np.log2(unique_chars) * length if unique_chars > 0 else 0

    # Basic heuristics
    if length < 6 or entropy < 20:
        return 0  # Weak
    elif 6 <= length < 10:
        if has_digit or has_upper or has_symbol:
            return 1  # Medium
        else:
            return 0  # Weak
    else:  # length >= 10
        if has_digit and has_symbol and has_upper and has_lower:
            return 2  # Strong
        elif has_digit and (has_upper or has_symbol):
            return 1  # Medium
        else:
            return 0  # Weak


# Label all passwords
print("[INFO] Labeling passwords based on heuristic rules...")
labeled = []
for pw in tqdm(passwords, total=len(passwords)):
    labeled.append((pw, rule_based_strength(pw)))

# Convert to DataFrame
df = pd.DataFrame(labeled, columns=["password", "strength"])

# Drop duplicates for efficiency
df = df.drop_duplicates(subset="password").reset_index(drop=True)

# Show distribution
counts = Counter(df["strength"])
total = sum(counts.values())
print("\n[INFO] Label Distribution:")
for k, v in sorted(counts.items()):
    pct = v / total * 100
    label = {0: "Weak", 1: "Medium", 2: "Strong"}[k]
    print(f"  {label:7s} → {v:,} ({pct:.2f}%)")

# Save labeled dataset
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ Saved labeled dataset to: {OUTPUT_PATH}")
