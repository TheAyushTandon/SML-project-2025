import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LABELED_PATH = os.path.join(DATA_DIR, "labeled", "combined.csv")
LEAK_PATH = os.path.join(DATA_DIR, "leaks", "rockyou.txt")
UNLABELED_PATH = os.path.join(DATA_DIR, "unlabeled", "xato.txt")
ROCKYOU_PATH = os.path.join("data", "leaks", "rockyou.txt")


MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_A_PATH = os.path.join(MODEL_DIR, "model_a_classifier.pkl")
MODEL_B_PATH = os.path.join("models", "hacker_risk_model.pkl")
MODEL_C_PATH = os.path.join(MODEL_DIR, "model_c_autoencoder.pt")
MODEL_D_PATH = os.path.join(MODEL_DIR, "model_d_generator.pt")

FREQ_TABLE_PATH = os.path.join(MODEL_DIR, "frequency_rank.csv")
