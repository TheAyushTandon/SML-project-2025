# src/models/hacker_risk.py
import os
import math
import pickle
from collections import Counter, defaultdict
import numpy as np
from rapidfuzz.distance import Levenshtein

# Helper: safe log
def _safe_log(x):
    return math.log(x + 1e-12)

class HackerRiskModel:
    """
    Hybrid hacker-risk scorer:
      - frequency/rank from leaks
      - char n-gram LM (smoothed)
      - edit-distance to top-K leaked passwords
      - structural heuristics (length, digits, symbols, entropy)
    Save model with .save(path) and load with HackerRiskModel.load(path).
    """

    def __init__(self, leak_path=None, top_k_for_edit=10000, ngram_n=3):
        self.leak_path = leak_path
        self.freq = Counter()
        self.total = 0
        self.rank_map = None  # password -> rank (1 = most frequent)
        self.unique_count = 0
        self.top_k_for_edit = top_k_for_edit
        self.top_k_list = []
        self.ngram_n = ngram_n
        self.ngram_counts = defaultdict(int)
        self.total_ngrams = 0

    # -------------------------
    # Build / load utilities
    # -------------------------
    def build_from_leaks(self):
        """Read leaked file, build freq distribution and ngram counts."""
        if not self.leak_path:
            raise ValueError("leak_path not set")

        with open(self.leak_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                pw = line.rstrip("\n")
                if pw == "":
                    continue
                self.freq[pw] += 1

        self.total = sum(self.freq.values())
        self.unique_count = len(self.freq)
        # rank map
        ordered = self.freq.most_common()
        self.rank_map = {pw: idx + 1 for idx, (pw, _) in enumerate(ordered)}
        # top-k list for edit-distance checks
        self.top_k_list = [pw for pw, _ in ordered[: self.top_k_for_edit]]

        # build ngram counts (char-level)
        n = self.ngram_n
        for pw, cnt in self.freq.items():
            s = f"<{pw}>"  # boundary markers
            for i in range(len(s) - n + 1):
                gram = s[i : i + n]
                self.ngram_counts[gram] += cnt
                self.total_ngrams += cnt

        return self

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "freq": self.freq,
                    "total": self.total,
                    "rank_map": self.rank_map,
                    "unique_count": self.unique_count,
                    "top_k_list": self.top_k_list,
                    "ngram_counts": dict(self.ngram_counts),
                    "total_ngrams": self.total_ngrams,
                    "ngram_n": self.ngram_n,
                },
                f,
            )

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        m = cls()
        m.freq = Counter(data["freq"])
        m.total = data["total"]
        m.rank_map = data["rank_map"]
        m.unique_count = data["unique_count"]
        m.top_k_list = data["top_k_list"]
        m.ngram_counts = defaultdict(int, data["ngram_counts"])
        m.total_ngrams = data["total_ngrams"]
        m.ngram_n = data.get("ngram_n", 3)
        return m

    # -------------------------
    # Signals
    # -------------------------
    def freq_percentile(self, password):
        """Return 0..1 where 1 means most frequent (highest risk)."""
        if self.unique_count == 0 or password not in self.rank_map:
            return 0.0
        rank = self.rank_map[password]
        # percentile: 1 - (rank-1)/(unique_count-1)
        p = 1.0 - (rank - 1) / max(1, (self.unique_count - 1))
        return float(p)

    def lm_logprob(self, password):
        """Compute average (per-char) log-prob under char ngram LM with add-1 smoothing.
           Higher (less negative) logprob => more likely under leaks => more risky.
        """
        n = self.ngram_n
        s = f"<{password}>"
        total_log = 0.0
        count = 0
        V = len(self.ngram_counts)  # approx vocab
        for i in range(len(s) - n + 1):
            gram = s[i : i + n]
            c = self.ngram_counts.get(gram, 0)
            # add-1 smoothing over counts
            prob = (c + 1) / (self.total_ngrams + V)
            total_log += math.log(prob)
            count += 1
        if count == 0:
            return -100.0
        avg = total_log / count
        return avg  # negative number, higher is "less negative" => more risky

    def min_edit_distance_topk(self, password, k=200):
        """Return normalized closeness to top-k leaks (0..1) where 1 means exact match (distance 0)."""
        # take min normalized distance
        best = 1.0
        # search a smaller top-k to be fast; ensure k <= available
        k = min(k, len(self.top_k_list))
        for pw in self.top_k_list[:k]:
            d = Levenshtein.distance(password, pw)
            # normalized distance by max length
            nd = d / max(1, max(len(password), len(pw)))
            if nd < best:
                best = nd
                if best == 0.0:
                    break
        return 1.0 - best  # invert so 1.0 means exact or near match

    def structural_score(self, password):
        """Simple structural heuristics normalized to 0..1 (higher => riskier)."""
        if not password:
            return 0.0
        length = len(password)
        digits = sum(c.isdigit() for c in password)
        symbols = sum(not c.isalnum() for c in password)
        unique = len(set(password))
        # Shannon-ish proxy:
        entropy = math.log2(unique + 1) * length if length > 0 else 0
        # heuristics: shorter & low entropy => risky
        # We'll map onto 0..1 (1 is risky)
        length_score = 1.0 if length <= 6 else (0.6 if length <= 8 else 0.2)
        digit_score = 0.8 if digits == 0 else 0.2
        symbol_score = 0.8 if symbols == 0 else 0.1
        entropy_score = 1.0 if entropy < 20 else 0.2
        # combine
        s = 0.4 * length_score + 0.2 * digit_score + 0.2 * symbol_score + 0.2 * entropy_score
        return min(1.0, max(0.0, s))

    # -------------------------
    # Final combined score
    # -------------------------
    def compute_score(self, password, weights=None):
        """
        Return a 0–100 hackability score (higher = riskier).
        Balanced for both leaked and strong unseen passwords.
        """
        if weights is None:
            weights = {"freq": 0.4, "lm": 0.25, "edit": 0.15, "struct": 0.20}

        # Core signals
        freq_p = self.freq_percentile(password)
        lm_lp = self.lm_logprob(password)
        lm_norm = 1.0 / (1.0 + math.exp(-(lm_lp + 4.5)))  # typical range ~[0,1]
        edit_sim = self.min_edit_distance_topk(password, k=1000)
        struct = self.structural_score(password)

        # Weighted risk components
        combined = (
            weights["freq"] * freq_p +
            weights["lm"] * lm_norm +
            weights["edit"] * edit_sim +
            weights["struct"] * struct
        )

        # Boost risk for exact leaked matches
        if password in self.freq:
            combined = max(combined, 0.95)

        # --- Complexity / Strength bonus (reduces risk) ---
        length = len(password)
        unique_chars = len(set(password))
        symbols = sum(not c.isalnum() for c in password)
        digits = sum(c.isdigit() for c in password)
        variety_bonus = (unique_chars / max(1, length)) * 0.4
        length_bonus = min(0.4, (length - 8) * 0.02) if length > 8 else 0
        symbol_bonus = 0.2 if symbols > 0 else 0
        digit_bonus = 0.1 if digits > 0 else 0
        complexity_bonus = variety_bonus + length_bonus + symbol_bonus + digit_bonus

        # Apply complexity: strong passwords reduce risk
        adjusted = combined * (1 - complexity_bonus)
        adjusted = max(0, min(1, adjusted))

        # Nonlinear scaling for better human readability
        risk_score = (adjusted ** 0.6) * 100
        risk_score = 20 + (risk_score * 0.8)
        risk_score = float(max(0, min(100, risk_score)))

        explain = {
            "freq_percentile": round(freq_p, 4),
            "lm_norm": round(lm_norm, 4),
            "edit_sim_topk": round(edit_sim, 4),
            "struct_score": round(struct, 4),
            "complexity_bonus": round(complexity_bonus, 3),
            "adjusted_combined": round(adjusted, 3),
        }

        return risk_score, explain


