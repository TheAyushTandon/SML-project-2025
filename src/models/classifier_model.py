import joblib
import numpy as np
import pandas as pd
from src.features.extractors import extract_features

class PasswordClassifier:
    def __init__(self, model):
        self.model = model

    @classmethod
    def load(cls, path):
        model = joblib.load(path)
        return cls(model)

    def predict(self, password):
        feat_dict = extract_features(password)
        # Match training process: np.array([extract_features(pw) for pw in passwords])
        # When sklearn receives object array of dicts, it converts to DataFrame
        # and then to numpy. String columns might be encoded or processed.
        
        # Create DataFrame from dict (matching sklearn's internal conversion)
        df = pd.DataFrame([feat_dict])
        
        # Get numeric features in the order they appear in extract_features
        numeric_cols = ['length', 'upper', 'lower', 'digits', 'special', 
                       'diversity', 'entropy', 'sequence_score']
        X_numeric = df[numeric_cols].values
        
        # If model expects more features than we have, pad with zeros
        # This handles cases where the model was trained with additional features
        if X_numeric.shape[1] < self.model.n_features_:
            # Pad with zeros to match expected feature count
            padding = np.zeros((1, self.model.n_features_ - X_numeric.shape[1]))
            X = np.hstack([X_numeric, padding])
        elif X_numeric.shape[1] > self.model.n_features_:
            # If we have more features, take only the first n_features_
            X = X_numeric[:, :self.model.n_features_]
        else:
            X = X_numeric
            
        feats = X.reshape(1, -1)
        pred = self.model.predict(feats)[0]
        probs = self.model.predict_proba(feats)[0]
        conf = max(probs)
        label = {0: "weak", 1: "medium", 2: "strong"}[pred]
        return label, conf
