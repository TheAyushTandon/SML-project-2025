# src/train/train_hacker_risk.py
import os
from src.models.hacker_risk import HackerRiskModel
from src.config import ROCKYOU_PATH, MODEL_B_PATH

def main():
    print("[INFO] Building hacker-risk artifacts...")
    m = HackerRiskModel(leak_path=ROCKYOU_PATH, top_k_for_edit=20000, ngram_n=3)
    m.build_from_leaks()
    os.makedirs(os.path.dirname(MODEL_B_PATH), exist_ok=True)
    m.save(MODEL_B_PATH)
    print(f"[✅] Hacker risk model saved -> {MODEL_B_PATH}")

if __name__ == "__main__":
    main()
