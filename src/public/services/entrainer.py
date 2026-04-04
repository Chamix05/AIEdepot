from services.log import extract_log
import joblib
import pandas as pd
import scipy.sparse as sp
from flask import render_template

def retrain_model():
    # Charger les objets de prétraitement
    vectorizer = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/vectorizer.pkl")
    vectorizer_subject = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/vectorizer_subject.pkl")
    vectorizer_coined = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/vectorizer_coined.pkl")
    scaler = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/scaler.pkl")
    encoder = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/encoder.pkl")

    bayes = joblib.load(r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/naive_bayes.pkl")

    # Extraire les emails classifiés
    logs = extract_log()
    df = pd.DataFrame(logs, columns=["sujet", "loginU", "resultat", "corps", "urls"])
    
   # -------------------------------
   # Recréer les colonnes manquantes
   # -------------------------------
    df["url_count"] = df["urls"].apply(lambda x: len(str(x).split(",")))
    df["url_has_login"] = df["urls"].apply(lambda x: int("login" in str(x).lower()))
    df["url_has_bank"] = df["urls"].apply(lambda x: int("bank" in str(x).lower()))
    df["url_has_secure"] = df["urls"].apply(lambda x: int("secure" in str(x).lower()))
    df["url_has_update"] = df["urls"].apply(lambda x: int("update" in str(x).lower()))
    df["url_avg_length"] = df["urls"].apply(
    lambda x: (sum(len(u) for u in str(x).split(",")) / len(str(x).split(","))) if x else 0
  )
    df["url_domains"] = df["urls"].apply(
    lambda x: len(set([u.split("/")[2] for u in str(x).split(",") if "://" in u]))
)

     # Colonnes manquantes
    df["has_attachment"] = 0
    df["sender_domain_suspicious"] = 0  # ou calculer comme dans ton script initial


    X_subject = vectorizer_subject.transform(df["sujet"])
    X_body = vectorizer.transform(df["corps"])
    X_coined = sp.csr_matrix((len(df), 0))  # si pas de colonne Coined.Word

    X_other = df[[
    "url_count","url_has_login","url_has_bank","url_has_secure",
    "url_has_update","url_avg_length","url_domains",
    "has_attachment","sender_domain_suspicious"
      ]].values


    X = sp.hstack([X_body, X_subject, X_coined, sp.csr_matrix(X_other)])
    print(encoder.classes_)

    df["resultat_num"] = df["resultat"].apply(lambda x: 1 if x == "phishing" else 0)
    y = df["resultat_num"]


    # Réentraîner
    bayes.fit(X, y)
    joblib.dump(bayes, r"C:/Users/DELL/Documents/Phishing_PRJ-c2/src/models/naive_bayes.pkl")

    # Préparer la notification
    notif_message = "Modèle Naive Bayes réentraîné avec succès!"
    notif_type = "success"

    # Retourner vers le dashboard avec notif
    return render_template(
        "dashboard.html",
        notif_message=notif_message,
        notif_type=notif_type
    )
