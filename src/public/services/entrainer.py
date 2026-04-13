import pandas as pd
import joblib
from .log import extract_log
from flask import render_template
import subprocess

def retrain_model():
    # Charger dataset initial
    bdd = pd.read_csv("Phishing_PRJ-c2/src/dataset/merged_dataset.csv")
    bayes = joblib.load("Phishing_PRJ-c2/src/models/naive_bayes.pkl")

    # Charger les logs
    logs = extract_log()
    df_logs = pd.DataFrame(logs, columns=["sujet", "loginU", "resultat", "corps", "urls"])
    df_logs["target"] = df_logs["resultat"].apply(lambda x: 1 if x == "phishing" else 0)

    # Harmoniser les colonnes avec le dataset initial
    df_logs.rename(columns={"sujet":"subject","corps":"body"}, inplace=True)
    df_logs["Coined.Word"] = ""
    df_logs["sender"] = "unknown"

    # Fusionner
    bdd_full = pd.concat([bdd, df_logs], ignore_index=True)

    # Sauvegarder dataset enrichi
    bdd_full.to_csv("Phishing_PRJ-c2/src/dataset/merged_dataset.csv", index=False)

    # Relancer ton script de prétraitement complet
    subprocess.run(["python", "Phishing_PRJ-c2/src/dataset/processed/phishing_dataset.py"])

    # Sauvegarder le modèle mis à jour
    joblib.dump(bayes, "Phishing_PRJ-c2/src/models/naive_bayes.pkl")

    notif_message = "Modèle Naive Bayes réentraîné avec succès !"
    notif_type = "success"

    return render_template("dashboard.html",
                           notif_message=notif_message,
                           notif_type=notif_type)
