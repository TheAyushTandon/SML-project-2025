# src/inference/anomaly_detector.py

import torch
import numpy as np
from src.models.anomaly_model import PasswordAutoencoder

def anomaly_score(features, model_path, threshold=0.015):
    model = PasswordAutoencoder(input_dim=len(features))
    model.load_state_dict(torch.load(model_path))
    model.eval()

    x = torch.FloatTensor(features).unsqueeze(0)
    with torch.no_grad():
        reconstructed = model(x)
    mse = torch.mean((x - reconstructed) ** 2).item()

    if mse > threshold:
        return {"status": "Anomalous (weak/unusual)", "score": mse}
    else:
        return {"status": "Normal (balanced structure)", "score": mse}
