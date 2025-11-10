# ============================================================
# src/test/test_classifier.py
# ------------------------------------------------------------
# Tests the trained Password Strength Classifier (Model A)
# ============================================================

import os
import sys
import numpy as np
import joblib

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.features.extractors import extract_features
from src.config import MODEL_A_PATH


def load_model(model_path=MODEL_A_PATH):
    """Load the trained LightGBM classifier"""
    print(f"[INFO] Loading model from: {model_path}")
    model = joblib.load(model_path)
    return model


def predict_password_strength(model, password):
    """Predict password strength category (0=Weak, 1=Medium, 2=Strong)"""
    features = np.array(extract_features(password)).reshape(1, -1)
    pred = model.predict(features)[0]
    probs = model.predict_proba(features)[0]

    labels = {0: "Weak", 1: "Medium", 2: "Strong"}
    print(f"\nPassword: {password}")
    print(f"Prediction: {labels[pred]}")
    print(f"Confidence: {probs[pred]*100:.2f}%")
    print(f"Class Probabilities: Weak={probs[0]:.3f}, Medium={probs[1]:.3f}, Strong={probs[2]:.3f}")
    return pred


def main():
    model = load_model()

    # Interactive testing
    print("\n[INFO] Enter passwords to test the classifier.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        password = input("🔹 Enter a password: ").strip()
        if password.lower() in ["exit", "quit"]:
            print("\n[INFO] Exiting test session.")
            break

        try:
            predict_password_strength(model, password)
        except Exception as e:
            print(f"[ERROR] Failed to predict: {e}")


if __name__ == "__main__":
    main()
