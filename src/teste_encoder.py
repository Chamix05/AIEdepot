import joblib

encoder = joblib.load(r"C:/Users/LAPTA/Documents/M1ASR/M1 S2/PROJ AIE/vsfinale/Phishing_PRJ-c2/src/models/encoder.pkl")
print("Classes connues par l'encoder :", encoder.classes_)

# Test de transformation
print("'unknown' est-il dedans ?", "unknown" in encoder.classes_)