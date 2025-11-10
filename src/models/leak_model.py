import math
import torch
from src.config import LEAK_PATH

class LeakRiskScorer:
    def __init__(self, freq_table=None):
        self.freq_table = freq_table or self._load_leak_table()

    def _load_leak_table(self):
        freq = {}
        with open(LEAK_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                pw = line.strip()
                if pw:
                    freq[pw] = i + 1
        return freq

    def score(self, password):
        """Compute hackability score based on frequency rank."""
        rank = self.freq_table.get(password)
        if rank:
            risk = 100 * (1 - math.log(rank + 1) / math.log(10**7))
            return min(max(risk, 0), 100)
        else:
            return 20  # assume low risk if unseen
    