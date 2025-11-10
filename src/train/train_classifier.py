# ============================================================
# src/train/train_classifier.py
# ------------------------------------------------------------
# Trains the Supervised Password Strength Classifier (Model A)
# ============================================================

import os
import sys
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump
from collections import Counter
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import matplotlib.pyplot as plt
import seaborn as sns

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.features.extractors import extract_features
from src.config import LABELED_PATH, MODEL_A_PATH


def main():
    # ============================================================
    # 1. Load & clean dataset
    # ============================================================
    print("[INFO] Loading labeled dataset...")

    # Prefer combined dataset if exists
    combined_path = os.path.join("data", "labeled", "combined.csv")
    data_path = combined_path if os.path.exists(combined_path) else LABELED_PATH

    df = pd.read_csv(data_path, on_bad_lines='skip', encoding='utf-8', engine='python')
    print(f"[INFO] Loaded dataset: {data_path}")
    print(f"[INFO] Dataset shape before cleaning: {df.shape}")

    # Drop missing or invalid rows
    df = df.dropna(subset=["password", "strength"]).reset_index(drop=True)
    df["password"] = df["password"].astype(str)

    print(f"[INFO] Dataset shape after cleaning: {df.shape}")

    # Label distribution check
    print("\n[INFO] Label Distribution (Raw Counts):")
    print(df["strength"].value_counts())

    print("\n[INFO] Label Distribution (Normalized):")
    print(df["strength"].value_counts(normalize=True).round(3))

    # Optional: sample to speed up training (uncomment if too slow)
    # df = df.sample(n=1_000_000, random_state=42)
    # print(f"[INFO] Using sampled subset: {df.shape}")

    # ============================================================
    # 2. Extract features
    # ============================================================
    print("\n[INFO] Extracting features...")
    X = np.array([extract_features(pw) for pw in df["password"]])
    y = df["strength"].astype(int).values

    # ============================================================
    # 3. Split into train/test (stratified)
    # ============================================================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ============================================================
    # 4. Handle imbalance (partial over/under-sampling)
    # ============================================================
    label_counts = Counter(y_train)
    max_count = max(label_counts.values())
    imbalance_ratio = max_count / min(label_counts.values())
    print(f"\n[INFO] Label counts (train): {label_counts}")
    print(f"[INFO] Imbalance ratio: {imbalance_ratio:.2f}x")

    if imbalance_ratio > 3.0:
        print("[⚠️] Severe imbalance detected — applying smart balancing strategy...")

        # Define target sizes
        target_counts = {
            cls: int(0.5 * max_count) if count < 0.5 * max_count else count
            for cls, count in label_counts.items()
        }
        print(f"[INFO] Target counts after rebalancing: {target_counts}")

        ros = RandomOverSampler(sampling_strategy=target_counts, random_state=42)
        rus = RandomUnderSampler(
            sampling_strategy={
                max(label_counts, key=label_counts.get): int(0.8 * max_count)
            },
            random_state=42,
        )

        rebalance = ImbPipeline(
            [
                ("undersample_majority", rus),
                ("oversample_minorities", ros),
            ]
        )

        X_train, y_train = rebalance.fit_resample(X_train, y_train)
        print(f"[INFO] New label counts after balancing: {Counter(y_train)}")

    else:
        print("[INFO] Label distribution acceptable — no rebalancing applied.")

    # ============================================================
    # 5. Train classifier
    # ============================================================
    print("[INFO] Training LightGBM classifier...")
    model = LGBMClassifier(
        n_estimators=200,          # slightly reduced for faster training
        learning_rate=0.08,
        max_depth=6,
        num_leaves=25,
        reg_alpha=0.4,
        reg_lambda=0.4,
        subsample=0.9,
        colsample_bytree=0.9,
        class_weight="balanced",
        n_jobs=-1,                # use all cores
        random_state=42
    )

    model.fit(X_train, y_train)
    print("[INFO] Training complete!")

    # ============================================================
    # 6. Evaluate & visualize
    # ============================================================
    preds = model.predict(X_test)

    print("\n[INFO] Classification Report:")
    print(classification_report(y_test, preds, digits=3))

    cm = confusion_matrix(y_test, preds)
    print("\n[INFO] Confusion Matrix:")
    print(cm)

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Weak", "Medium", "Strong"],
        yticklabels=["Weak", "Medium", "Strong"],
    )
    plt.title("Password Strength Classifier - Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    os.makedirs(os.path.dirname(MODEL_A_PATH), exist_ok=True)
    png_path = os.path.join(os.path.dirname(MODEL_A_PATH), "confusion_matrix.png")
    plt.savefig(png_path, bbox_inches="tight")
    plt.close()
    print(f"[✅] Confusion matrix saved to: {os.path.abspath(png_path)}")

    # ============================================================
    # 7. Save model
    # ============================================================
    dump(model, MODEL_A_PATH)
    print(f"[✅] Model saved to: {os.path.abspath(MODEL_A_PATH)}")


if __name__ == "__main__":
    main()
