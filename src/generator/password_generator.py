# ============================================================
# src/generator/password_generator.py
# ------------------------------------------------------------
# Generates strong yet memorable passwords based on a user’s
# input word or phrase (Model D - Generator)
# ============================================================

import random
import re
import string
from typing import Dict
import os
import sys

# Optional: if you later want to re-enable ensemble scoring,
# you can uncomment these two lines:
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# from backend.ensemble import evaluate_password  # <- disabled to avoid circular import

# ------------------------------------------------------------
# 🔹 Leetspeak map and symbol pools
# ------------------------------------------------------------
LEET_MAP = {
    "a": ["@", "4"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["$", "5"],
    "t": ["7"],
    "g": ["9"],
}

SYMBOL_POOL = list("!@#$%&*?+-=_")

# ------------------------------------------------------------
# 🔹 Helper transformations
# ------------------------------------------------------------
def random_capitalize(word: str) -> str:
    """Randomly capitalize ~40% of characters."""
    return "".join(
        c.upper() if random.random() < 0.4 else c.lower() for c in word
    )

def leetspeak(word: str) -> str:
    """Replace letters with leetspeak equivalents."""
    return "".join(
        random.choice(LEET_MAP[c.lower()])
        if c.lower() in LEET_MAP and random.random() < 0.6
        else c
        for c in word
    )

def inject_symbols(word: str) -> str:
    """Randomly inject a symbol into the word."""
    if random.random() < 0.7 and len(word) > 1:
        pos = random.randint(1, len(word) - 1)
        sym = random.choice(SYMBOL_POOL)
        word = word[:pos] + sym + word[pos:]
    return word

def add_affix(word: str) -> str:
    """Add random prefix/suffix digits or symbols."""
    suffix = str(random.randint(10, 99))
    if random.random() < 0.5:
        prefix = random.choice(["X", "Z", "Q", "P"]) + str(random.randint(1, 9))
        return prefix + word + suffix
    return word + suffix

def ensure_entropy(pw: str) -> str:
    """Guarantee password includes at least one uppercase, digit, and symbol."""
    if not any(c.isupper() for c in pw):
        pw += random.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in pw):
        pw += random.choice(string.digits)
    if not any(c in string.punctuation for c in pw):
        pw += random.choice(SYMBOL_POOL)
    return pw

# ------------------------------------------------------------
# 🔹 Main Generator Function
# ------------------------------------------------------------
def generate_password(base: str, n_variants: int = 5) -> Dict:
    """
    Generate multiple strong passwords from a base keyword.
    Returns dictionary with best suggestion and full list.

    Args:
        base (str): user-provided word or phrase.
        n_variants (int): number of variants to generate.

    Returns:
        dict: containing base word, suggestions, and best password.
    """
    base = re.sub(r"\s+", "", base.strip())
    if len(base) < 3:
        raise ValueError("Base word too short. Use at least 3 letters.")

    candidates = []
    for _ in range(n_variants):
        pw = base
        pw = random_capitalize(pw)
        pw = leetspeak(pw)
        pw = inject_symbols(pw)
        pw = add_affix(pw)
        pw = ensure_entropy(pw)
        candidates.append(pw)

    # ⚙️ Placeholder ranking logic (can be upgraded to use ensemble later)
    # For now, pick the most diverse-looking password as "best"
    def entropy_approx(pw):
        charset = len(set(pw))
        return charset / len(pw)

    ranked = sorted(candidates, key=entropy_approx, reverse=True)
    best_pw = ranked[0]

    return {
        "base": base,
        "suggestions": ranked,
        "best_password": best_pw,
    }

# ------------------------------------------------------------
# 🔹 CLI Demo
# ------------------------------------------------------------
if __name__ == "__main__":
    base = input("Enter a word or phrase to base your password on: ").strip()
    result = generate_password(base, n_variants=5)

    print("\nGenerated Passwords:")
    for p in result["suggestions"]:
        print(f"  → {p}")
    print(f"\nBest Password: {result['best_password']}")
