# src/unsupervised/evaluate_detector.py
import numpy as np
from pathlib import Path
from .detector import score_password, encode_pwd, extract_struct_features
import json

def scan_sample_file(sample_path, n=10000):
    with open(sample_path, "r", encoding="utf-8", errors="ignore") as f:
        pwds = [line.strip() for i,line in enumerate(f) if i<n]
    scores = [score_password(pw)["anomaly_score"] for pw in pwds]
    return scores, pwds

if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parents[2]
    sample = ROOT / "data" / "xato" / "10-million-passwords.txt"
    print("[INFO] Sampling...")
    s, p = scan_sample_file(sample, n=5000)
    import numpy as np
    print("mean", np.mean(s), "median", np.median(s))
    # pick threshold at e.g. 98th percentile for anomaly flagging
    th = np.percentile(s, 98)
    print("suggested threshold (98 pct):", th)
