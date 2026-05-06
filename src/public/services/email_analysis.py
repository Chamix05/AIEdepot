import os, re, email,json
from tempfile import template
import joblib
import scipy.sparse as sp
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from ..db_connection import get_connection
import numpy as np
import random


pipeline = joblib.load("src/models/pipeline.pkl")
bayes = joblib.load("src/models/naive_bayes.pkl")


vectorizer_body = pipeline["vectorizer_body"]
vectorizer_subject = pipeline["vectorizer_subject"]
vectorizer_coined = pipeline["vectorizer_coined"]
encoder = pipeline["encoder"]
scaler = pipeline["scaler"]

with open("src/public/services/coined_word.json", "r", encoding="utf-8") as f:
    coined_dict = json.load(f)

phishing_words = set(coined_dict["phishing_words"])
legit_words = set(coined_dict["legit_words"])
ambiguous_words = set(coined_dict["ambiguous_words"])


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
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

with open(os.path.join(ROOT_DIR, "C:/Users/LAPTA/Documents/M1ASR/M1 S2/PROJ AIE/vsfinale/Phishing_PRJ-c2/src/dataset/trusted_domains.json"), "r", encoding="utf-8") as f:
    trusted_domains = json.load(f)
#with open("src/dataset/trusted_domains.json", "r", encoding="utf-8") as f:
 #   trusted_domains = json.load(f)


#Vérifie si le domaine de l’expéditeur correspond à celui des URLs.
#cette fonction sert à vérifier si les liens dans l’email pointent bien vers le même domaine que 
# l’expéditeur
def is_domain_consistent(sender, urls):
    sender_domain = sender.split("@")[-1]
    for u in urls:
        try:
            domain = u.split("/")[2]
            if sender_domain in domain:
                return True
        except:
            continue
    return False




#Vérifie si l’expéditeur correspond à une marque connue mais avec un domaine non autorisé
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
    



def get_sender(filepath: str) -> str:
    """Récupérer l'expéditeur d'un email .eml, même si le champ 'From' est absent"""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        msg = email.message_from_file(f)
    
    # Essayer d'abord l'en-tête standard
    sender = msg.get("from")
    if sender:
        return sender.strip()
    
    # Si pas d'en-tête 'From', lire le contenu brut et prendre la dernière ligne
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
        if lines:
            last_line = lines[-1].strip()
            return last_line if last_line else "unknown"
    
    return "unknown"


    text = (subject + " " + body).lower().split()
    phishing_detected = [w for w in text if w in phishing_words]
    legit_detected = [w for w in text if w in legit_words]
    return " ".join(phishing_detected), " ".join(legit_detected)
def extract_coined_words(subject: str, body: str) -> str:
    """
    Retourne une chaîne contenant les mots détectés
    (phishing ou légitimes) présents dans l'email.
    """
    text = (subject + " " + body).lower().split()
    keywords = [w for w in text if w in phishing_words or w in legit_words]
    return " ".join(keywords)


def analyze_email(filename: str, loginU: str) -> tuple[str, str]:
    """Pipeline complet d'analyse d'un email uploadé"""
    filepath = os.path.join("uploads", filename)
    subject, body, sender = extract_email(filepath)

    # Nettoyage
    subject_clean = clean_text(subject)
    body_clean = clean_text(body)
    sender_normal=get_sender(filepath)

    # URLs
    urls = re.findall(r'\b(?:[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+|www\.[^\s]+)', body)
    url_count = len(urls)
    url_avg_length = int(sum(len(u) for u in urls) / url_count) if url_count > 0 else 0
    url_domains = len(set([u.split("/")[2] for u in urls if "://" in u]))
    sender_domain_suspicious = is_suspicious_sender(sender)
    domain_consistent = is_domain_consistent(sender, urls)
    coined_clean = clean_text(extract_coined_words(subject_clean, body_clean))
    X_coined = vectorizer_coined.transform([coined_clean])


    # Features numériques (exactement comme au prétraitement)
    features = [[url_count, url_avg_length, url_domains,
                 sender_domain_suspicious]]
    X_other = scaler.transform(features)

    # Encodage expéditeur
    sender_encoded = safe_encode_sender(sender, encoder)

    # Fusionner toutes les features
    X = sp.hstack([
        vectorizer_body.transform([body_clean]),
        vectorizer_subject.transform([subject_clean]),
        X_coined,
        sp.csr_matrix([sender_encoded]).T,
        sp.csr_matrix(X_other)
    ])
    


    # Prédiction avec seuil ajusté
    y_pred = bayes.predict(X).item()
    if y_pred==0:
        prediction = "legitime"  
    else:
        prediction = "phishing" 
        
    legit_detected = list(set([w for w in body_clean.split() if w in legit_words]))
    phishing_detected = list(set([w for w in body_clean.split() if w in phishing_words]))
    ambiguous_detected = list(set([w for w in body_clean.split() if w in ambiguous_words]))

    suspicion_score = 0
    if sender_domain_suspicious == 1:
     suspicion_score += 0.5
    if not domain_consistent:
     suspicion_score += 0.5
    if url_count > 2 or url_avg_length > 100:
     suspicion_score += 1
   
         
    # Pondération des mots
    if len(phishing_detected) >= 2:
     suspicion_score += 3
    if len(ambiguous_detected) >= 2:
     suspicion_score += 0.25 # 1 faible poids 
    if len(legit_detected) >= 2:
     suspicion_score -= 1  #0.5 réduit le score si beaucoup de mots légitimes
     
     # Bonus si mot critique dans le subject
     # critical_subject_words = ["urgent", "suspend", "secure-login", "account", "immediate", "immediately"]
     #if any(word in subject_clean for word in critical_subject_words):
      #suspicion_score += 2   # poids fort mais pas verdict direct
     
    # Décision finale
    if suspicion_score >= 4:
      resultat = "phishing"
    elif suspicion_score <= 0:
      resultat = "legitime"
    else:
     resultat = prediction  # laisse le modèle décider si score neutre

    
    if sender_normal == "unknown" and suspicion_score < 2 and not phishing_detected:
     resultat = "legitime"


     
    save_email(subject, body, urls, loginU, resultat)
    
    templates = [
    "L'expression {w} est repérée, fréquemment associée à des emails frauduleux."
      ]
    
    extra_li = ""
    if resultat == "legitime":
       extra_li += "<li class='list-group-item'>✅ Cet email ne présente aucun risque particulier</li>"
    
     # Si des mots légitimes ont été détectés
       #legit_detected = [w for w in body_clean.split() if w in legit_words]
       if legit_detected:
         words_legit_str = ", ".join(set(legit_detected))
         extra_li += f"<li class='list-group-item'>✅ Mots légitimes détectés : {words_legit_str}</li>"
    
      # Vérification des URLs
       if url_count <= 2 and url_avg_length < 100 and domain_consistent:
        extra_li += "<li class='list-group-item'>✅ Les URLs sont peu nombreuses, cohérentes et de longueur normale</li>"
       else:
        extra_li += "<li class='list-group-item'>⚠️ Attention : certaines caractéristiques des URLs méritent une vérification</li>"
    else:  # resultat == "phishing"
        #phishing_detected = [w for w in body_clean.split() if w in phishing_words]
        if not domain_consistent:
            if phishing_detected:
                # Joindre tous les mots trouvés en une seule ligne
                words_str = ", ".join(set(phishing_detected))
                phrase = templates[0].format(w=words_str)
                extra_li += f"<li class='list-group-item'>⚠️ {phrase}</li>"
            else: 
                extra_li += "<li class='list-group-item'>⚠️ Aucun mot sensible détecté, mais l'email reste suspect.</li>"

        # Vérification des URLs
        if url_avg_length >= 100 or url_count > 2:
            extra_li += f"<li class='list-group-item'>⚠️ Les liens sont trop nombreux ou trop longs ({url_count} liens, longueur moyenne {url_avg_length} caractères)</li>"
  
        
    # Bloc HTML final
    explanation_html = f"""
   <ul class="list-group list-group-flush">
    <li class="list-group-item">Expéditeur : <strong>{sender_normal}</strong> → {"suspect" if sender_domain_suspicious else "non suspect"}</li>
     {extra_li}
    </ul>
    """
    

    return resultat, explanation_html
    
