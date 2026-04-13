import joblib

encoder = joblib.load(r"src/models/encoder.pkl")
print("Classes connues par l'encoder :", encoder.classes_)

# Test de transformation
print("'unknown' est-il dedans ?", "unknown" in encoder.classes_)