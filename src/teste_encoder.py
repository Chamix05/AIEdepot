import joblib

encoder = joblib.load(r"C:\\Users\DELL\Documents\\Phishing_PRJ-c2\src\\models\\encoder.pkl")
print("Classes connues par l'encoder :", encoder.classes_)

# Test de transformation
print("'unknown' est-il dedans ?", "unknown" in encoder.classes_)