import math
import re
import numpy as np

def compute_entropy(password: str):
    """Shannon entropy estimation."""
    if not password:
        return 0
    probs = [password.count(c) / len(password) for c in set(password)]
    return -sum(p * math.log2(p) for p in probs)

def clean_password(pw: str):
    """Simple cleaning (strip, lower)"""
    return pw.strip()

def has_common_pattern(pw: str):
    patterns = ["password", "12345", "qwerty", "admin", "letmein"]
    pw_lower = pw.lower()
    return any(p in pw_lower for p in patterns)
