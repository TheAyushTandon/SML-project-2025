import pandas as pd
import os

# === Define paths ===
LABELED_1 = os.path.join("data", "labeled", "data.csv")
LABELED_2 = os.path.join("data", "labeled", "xato_labeled.csv")
OUTPUT_PATH = os.path.join("data", "labeled", "combined.csv")

# === Load datasets safely ===
print("[INFO] Loading datasets...")
df1 = pd.read_csv(LABELED_1, on_bad_lines="skip", encoding="utf-8")
df2 = pd.read_csv(LABELED_2, on_bad_lines="skip", encoding="utf-8")

print(f"[INFO] Dataset 1 shape: {df1.shape}")
print(f"[INFO] Dataset 2 shape: {df2.shape}")

# === Keep only relevant columns ===
df1 = df1[["password", "strength"]]
df2 = df2[["password", "strength"]]

# === Merge datasets ===
df = pd.concat([df1, df2], ignore_index=True)

# === Clean ===
df = df.dropna(subset=["password", "strength"]).drop_duplicates(subset=["password"])
df["password"] = df["password"].astype(str)
df["strength"] = df["strength"].astype(int)

print(f"[INFO] Combined dataset shape: {df.shape}")

# === Label distribution ===
dist = df["strength"].value_counts(normalize=True).round(3) * 100
print("\n[INFO] Label Distribution (%):")
print(dist)

# === Save ===
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"\n✅ Saved combined dataset → {OUTPUT_PATH}")
