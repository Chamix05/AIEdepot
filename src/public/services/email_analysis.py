import os, re, email
import joblib
import scipy.sparse as sp
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from ..db_connection import get_connection
# Charger le modèle et les objets de prétraitement sauvegardés
bayes = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/naive_bayes.pkl")
vectorizer_body = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/vectorizer.pkl")
vectorizer_subject = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/vectorizer_subject.pkl")
vectorizer_coined = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/vectorizer_coined.pkl")
scaler = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/scaler.pkl")
encoder = joblib.load(r"C:/Users/DELL/images/Phishing_PRJ-c2/src/models/encoder.pkl")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """Nettoyage + lemmatisation du texte, en gardant les URLs et mots clés"""
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9:/.\s-]", "", text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(lemmatizer.lemmatize(w) for w in words)

def extract_email(filepath: str):
    """Lire un fichier .eml et extraire subject + body + sender"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        msg = email.message_from_file(f)
    subject = msg["subject"] or ""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode(errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(errors="ignore")
    return subject, body, msg.get("from", "unknown")

def safe_encode_sender(sender: str, encoder) -> int:
    """Encodage robuste de l'expéditeur avec fallback 'unknown'"""
    sender = str(sender).strip().lower()
    if sender in encoder.classes_:
        return encoder.transform([sender])[0]
    else:
        return encoder.transform(["unknown"])[0]

# Marques sensibles et domaines autorisés
trusted_domains = {
    "amazon": [
        r".*@([a-z0-9.-]+\.)?amazon\.[a-z]{2,}$",
        r"newsletter@amazon\.com$"
    ],
    "paypal": [r".*@([a-z0-9.-]+\.)?paypal\.[a-z]{2,}$"],
    "microsoft": [
        r".*@([a-z0-9.-]+\.)?microsoft\.[a-z]{2,}$",
        r".*@outlook\.[a-z]{2,}$"
    ],
    "google": [
        r".*@([a-z0-9.-]+\.)?google\.[a-z]{2,}$",
        r".*@gmail\.[a-z]{2,}$"
    ],
    "apple": [
        r".*@([a-z0-9.-]+\.)?apple\.[a-z]{2,}$",
        r".*@icloud\.[a-z]{2,}$"
    ],
    "facebook": [
        r".*@([a-z0-9.-]+\.)?facebook\.[a-z]{2,}$",
        r".*@meta\.[a-z]{2,}$"
    ],
    "twitter": [
        r".*@([a-z0-9.-]+\.)?twitter\.[a-z]{2,}$",
        r".*@x\.[a-z]{2,}$"
    ],
    "linkedin": [r".*@([a-z0-9.-]+\.)?linkedin\.[a-z]{2,}$"],
    "ebay": [r".*@([a-z0-9.-]+\.)?ebay\.[a-z]{2,}$"],
    "hsbc": [r".*@([a-z0-9.-]+\.)?hsbc\.[a-z]{2,}$"],
    "bankofamerica": [r".*@([a-z0-9.-]+\.)?bankofamerica\.[a-z]{2,}$"]
}



def is_domain_consistent(sender, urls):
    sender_domain = sender.split("@")[-1]
    for u in urls:
        try:
            domain = u.split("/")[2]
            if sender_domain not in domain:
                return False
        except:
            continue
    return True



def is_suspicious_sender(sender: str) -> int:
    sender = str(sender).strip().lower()
    for brand, patterns in trusted_domains.items():
        if brand in sender:
            if not any(re.match(p, sender) for p in patterns):
                return 1
    return 0


def save_email(subject, body, urls, loginU, resultat):
    db = get_connection()  # ta fonction qui ouvre la connexion
    cursor = db.cursor()
    

    # Insérer dans la table classe
    cursor.execute("""
        INSERT INTO classe (resultat, idlog)
        VALUES (%s, %s)
    """, (resultat, loginU))
     # Récupérer l'idc généré
    idc = cursor.lastrowid

    # Insérer dans la table email
    cursor.execute("""
        INSERT INTO email (corps, sujet, urls, piecesJ, loginU, idc)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (body, subject, ";".join(urls), None, loginU, idc))

    db.commit()
    cursor.close()
    db.close()

def analyze_email(filename: str, loginU: str) -> str:
    """Pipeline complet d'analyse d'un email uploadé"""
    filepath = os.path.join("uploads", filename)
    subject, body, sender = extract_email(filepath)

    # Nettoyage
    subject_clean = clean_text(subject)
    body_clean = clean_text(body)

    # URLs
    urls = re.findall(r"http[s]?://\S+", body)
    url_count = len(urls)
    url_has_login = int(any("login" in u.lower() for u in urls))
    url_has_bank = int(any("bank" in u.lower() for u in urls))
    url_has_secure = int(any("secure" in u.lower() for u in urls))
    url_has_update = int(any("update" in u.lower() for u in urls))
    url_avg_length = int(sum(len(u) for u in urls) / url_count) if url_count > 0 else 0
    url_domains = len(set([u.split("/")[2] for u in urls if "://" in u]))
    has_attachment = 0
    sender_domain_suspicious = is_suspicious_sender(sender)
    domain_consistent = is_domain_consistent(sender, urls)

    # Features numériques (exactement comme au prétraitement)
    features = [[url_count, url_has_login, url_has_bank, url_has_secure,
                 url_has_update, url_avg_length, url_domains,
                 has_attachment, sender_domain_suspicious]]
    X_other = scaler.transform(features)

    # Encodage expéditeur
    sender_encoded = safe_encode_sender(sender, encoder)

    # Fusionner toutes les features
    X = sp.hstack([
        vectorizer_body.transform([body_clean]),
        vectorizer_subject.transform([subject_clean]),
        vectorizer_coined.transform([""]),  # si pas de coined words
        sp.csr_matrix([sender_encoded]).T,
        sp.csr_matrix(X_other)
    ])

    # Prédiction
    #Donc tu as deux signaux qui se contredisent :
    #Le modèle ML dit phishing.
    #La règle métier dit légitime.
    prediction = bayes.predict(X)
    if prediction[0] == 1 and sender_domain_suspicious == 0 and domain_consistent:
    # Le modèle dit phishing mais l'expéditeur est whitelisté
      resultat ="legitime"
    else:
      resultat ="phishing" if prediction[0] == 1 else  "legitime"
     # Sauvegarde en base
     
    save_email(subject, body, urls, loginU, resultat)
    return resultat
