# ============================================================
# backend/app.py
# ------------------------------------------------------------
# Unified API for Password Strength, Leak Risk, Anomaly & Generator
# Compatible with Python 3.9 and FastAPI frontend integrations
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import torch
import numpy as np
import pandas as pd
from src.models.classifier_model import PasswordClassifier
from src.models.leak_model import LeakRiskScorer
from src.models.anomaly_model import PasswordAutoencoder
from src.generator.password_generator import generate_password
from src.features.extractors import extract_features
from src.config import MODEL_A_PATH, MODEL_C_PATH

# ------------------------------------------------------------
# Initialize FastAPI
# ------------------------------------------------------------
app = FastAPI(title="Password Safety API")

# ------------------------------------------------------------
# ✅ Enable CORS for Frontend Integration
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev
        "http://127.0.0.1:5173",
        "http://localhost:8501",  # Streamlit default
        "http://127.0.0.1:8501",
        "https://your-vercel-site.vercel.app",  # Production (optional)
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",  # Allow localhost on any port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ------------------------------------------------------------
# Load Models
# ------------------------------------------------------------
print("[INFO] Loading Model A (Classifier)...")
model_a = PasswordClassifier.load(MODEL_A_PATH)

print("[INFO] Loading Model B (Leak / Hacker Risk Scorer)...")
model_b = LeakRiskScorer()

print("[INFO] Loading Model C (Unsupervised Autoencoder)...")
model_c = PasswordAutoencoder(input_dim=8)
model_c.load_state_dict(torch.load(MODEL_C_PATH, map_location="cpu"))
model_c.eval()

print("[✅] All models loaded successfully.")

# ------------------------------------------------------------
# Request Schemas
# ------------------------------------------------------------
class PasswordReq(BaseModel):
    password: str


class PasswordBaseReq(BaseModel):
    base: Optional[str] = None
    length: Optional[int] = None
    mode: Optional[str] = "balanced"


# ------------------------------------------------------------
# Evaluate Password
# ------------------------------------------------------------
@app.post("/evaluate")
def evaluate(req: PasswordReq):
    pw = req.password.strip()

    # --- Model A ---
    a_label, a_conf = model_a.predict(pw)

    # --- Model B ---
    b_score = model_b.score(pw)
    leak_risk = {
        "score": round(b_score, 2),
        "is_leaked": b_score > 70,
        "message": (
            "⚠️ Found in common password leaks!" if b_score > 70
            else "✅ Not found in major leaks."
        ),
    }

    # --- Model C ---
    try:
        with torch.no_grad():
            recon_error = model_c.reconstruction_error(pw)
        anomaly_score = float(recon_error)
        anomaly_detection = {
            "score": anomaly_score,
            "is_anomaly": anomaly_score > 0.2,
            "reconstruction_error": anomaly_score,
        }
    except Exception:
        anomaly_detection = {
            "score": 0.1,
            "is_anomaly": False,
            "reconstruction_error": 0.1,
        }

    # --- Strength Mapping ---
    # a_label is already a string ("weak", "medium", "strong") from model_a.predict
    strength = a_label

    # --- Probabilities ---
    # Get actual probabilities from the model (using same method as predict)
    feat_dict = extract_features(pw)
    df = pd.DataFrame([feat_dict])
    
    # Get numeric features in the same order as classifier_model.predict
    numeric_cols = ['length', 'upper', 'lower', 'digits', 'special', 
                   'diversity', 'entropy', 'sequence_score']
    X_numeric = df[numeric_cols].values
    
    # Pad or truncate to match model's expected feature count
    if X_numeric.shape[1] < model_a.model.n_features_:
        padding = np.zeros((1, model_a.model.n_features_ - X_numeric.shape[1]))
        feats = np.hstack([X_numeric, padding]).reshape(1, -1)
    elif X_numeric.shape[1] > model_a.model.n_features_:
        feats = X_numeric[:, :model_a.model.n_features_].reshape(1, -1)
    else:
        feats = X_numeric.reshape(1, -1)
    
    probs = model_a.model.predict_proba(feats)[0]
    classifier_probabilities = {
        "weak": round(probs[0], 3),
        "medium": round(probs[1], 3),
        "strong": round(probs[2], 3),
    }

    # --- Feedback ---
    feedback = []
    if strength == "weak":
        feedback.append("Use a mix of uppercase, lowercase, digits, and symbols.")
    if b_score > 60:
        feedback.append("Avoid passwords found in breach databases.")
    if anomaly_detection["is_anomaly"]:
        feedback.append("Try a less predictable pattern.")

    return {
        "strength": strength,
        "classifier_probabilities": classifier_probabilities,
        "leak_risk": leak_risk,
        "anomaly_detection": anomaly_detection,
        "feedback": feedback,
    }


# ------------------------------------------------------------
# Generate Passwords
# ------------------------------------------------------------
@app.post("/generate_password")
def generate_pw(req: PasswordBaseReq):
    base_word = req.base.strip() if req.base else "sentinel"

    try:
        result = generate_password(base_word)
        return {"passwords": result["suggestions"]}
    except Exception as e:
        return {"passwords": [f"Error: {str(e)}"]}


# ------------------------------------------------------------
# Root Endpoint
# ------------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "🔐 Password Safety API is running!",
        "endpoints": ["/evaluate", "/generate_password"],
    }
