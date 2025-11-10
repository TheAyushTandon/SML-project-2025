from src.features.extractors import generate_features

password_samples = [
    "password123", "admin", "letmein", "Qwerty@123", "S3cur3!Pass",
    "abc12345", "MyName@2025", "Pa$$w0rd!", "12345678", "Hello_World99"
]

generate_features(password_samples)
