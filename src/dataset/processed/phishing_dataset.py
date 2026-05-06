import os, re
from flask import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder,  MinMaxScaler
import scipy.sparse as sp
import joblib
from sklearn.naive_bayes import MultinomialNB


# Charger le dataset fusionné
bdd = pd.read_csv("src/dataset/merged_dataset.csv")
print(bdd.columns)
print(bdd.head())

# Nettoyage des colonnes inutiles
bdd_clean = bdd.drop(columns=[
    "receiver","Email_Subject","Email_Content","Sending_Date","Sender_Title",
    "Sending_Time","Sender_Name","label","Sender_Email ","Day","URL_Title",
    "date","To","Closing_Remarks","Logo"
])

# Imputation des colonnes textuelles
for col in ["sender","subject","body","Coined.Word"]:
    if col in bdd_clean.columns:
        if not bdd_clean[col].mode().empty:
            bdd_clean[col] = bdd_clean[col].fillna(bdd_clean[col].mode()[0])
        else:
            bdd_clean[col] = bdd_clean[col].fillna("Unknown")

# Imputation colonnes numériques
if "urls" in bdd_clean.columns and not bdd_clean["urls"].mode().empty:
    bdd_clean["urls"] = bdd_clean["urls"].fillna(bdd_clean["urls"].mode()[0])


# -------------------------------
# Nettoyage et lemmatisation
# -------------------------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = str(text).lower()
    # garder lettres, chiffres, :, /, ., - (pour ne pas casser les URLs)
    text = re.sub(r"[^a-zA-Z0-9:/.\s-]", "", text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(lemmatizer.lemmatize(w) for w in words)

for col in ["subject","body","Coined.Word"]:
    bdd_clean[col] = bdd_clean[col].fillna("").apply(clean_text)

# -------------------------------
# Vectorisation TF-IDF
# -------------------------------
vectorizer_body = TfidfVectorizer(max_features=1000)
X_text = vectorizer_body.fit_transform(bdd_clean["body"])

vectorizer_subject = TfidfVectorizer(max_features=200)
X_subject = vectorizer_subject.fit_transform(bdd_clean["subject"])

#vectorizer_coined = TfidfVectorizer(max_features=200)
vectorizer_coined = TfidfVectorizer(max_features=300)
X_coined = vectorizer_coined.fit_transform(bdd_clean["Coined.Word"])

# -------------------------------
# Encodage expéditeur
# -------------------------------

encoder = LabelEncoder()
all_senders = list(bdd_clean["sender"].astype(str)) + ["unknown"]
encoder.fit(all_senders)
sender_encoded = encoder.transform(bdd_clean["sender"].astype(str))

# -------------------------------
# Features sur les URLs
# -------------------------------

urls_col = bdd_clean["urls"].fillna("").astype(str)

# nombre de liens dans l’email
bdd_clean["url_count"] = urls_col.apply(lambda x: len(x.split(",")) if x != "" else 0)

#longueur moyenne des liens
bdd_clean["url_avg_length"] = urls_col.apply(
    lambda x: (sum(len(u) for u in x.split(",")) / len(x.split(","))) if x != "" else 0
)

#nombre de domaines différents
bdd_clean["url_domains"] = urls_col.apply(
    lambda x: len(set([u.split("/")[2] for u in x.split(",") if "://" in u]))
)



# Marques sensibles et domaines autorisés
with open("src/dataset/trusted_domains.json", "r", encoding="utf-8") as f:
    trusted_domains = json.load(f)


def is_suspicious_sender(sender: str) -> int:
    sender = str(sender).strip().lower()
    for brand, patterns in trusted_domains.items():
        if brand in sender:
            if not any(re.match(p, sender) for p in patterns):
                return 1
    return 0

bdd_clean["sender_domain_suspicious"] = bdd_clean["sender"].apply(is_suspicious_sender)



# -------------------------------
# Normalisation des features numériques
# -------------------------------

scaler = MinMaxScaler()
X_other = scaler.fit_transform(
    bdd_clean[["url_count","url_avg_length","url_domains",
               "sender_domain_suspicious"]]
)

# -------------------------------
# Fusion des features
# -------------------------------

X = sp.hstack([X_text, X_subject, X_coined,
               sp.csr_matrix(sender_encoded).T,
               sp.csr_matrix(X_other)])




#Sauvegarde du dataset prétraité

X_df = pd.DataFrame(X.toarray())
X_df["target"] = bdd_clean["target"].values
X_df.to_csv(
    "src/dataset/processed/dataset_pretraite_vect.csv",
    index=False
)


# Sauvegarde pipeline complet

pipeline = {
    "vectorizer_body": vectorizer_body,
    "vectorizer_subject": vectorizer_subject,
    "vectorizer_coined": vectorizer_coined,
    "encoder": encoder,
    "scaler": scaler
}
joblib.dump(pipeline, "src/models/pipeline.pkl")
print("Pipeline sauvegardé avec", X.shape[1], "features")


