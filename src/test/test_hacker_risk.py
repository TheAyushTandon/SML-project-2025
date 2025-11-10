# src/test/test_hacker_risk.py
from src.models.hacker_risk import HackerRiskModel
from src.config import MODEL_B_PATH

m = HackerRiskModel.load(MODEL_B_PATH)
samples = [
    "123456", "password", "qwerty123", "helloWORLD", "Myp@ssword99!", "L0v3C@t$2025", "Hello",
    "ayush1234", "p@ssword", "S0m3Rand0m#Chars!", "WordGame", "fbeiabiq83791brob*^%#@@()"
]
for s in samples:
    score, explain = m.compute_score(s)
    print(f"{s:18} -> {score:.1f} | {explain}")
