import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.feature_extraction.text import CountVectorizer

# Charger plusieurs fichiers CSV
df1 = pd.read_csv("src/dataset/brute/CEAS_08.csv", encoding="latin1")
df2 = pd.read_csv("src/dataset/brute/Enron.csv", encoding="latin1")
df3= pd.read_csv("src/dataset/brute/Nazario.csv", encoding="latin1")
df4= pd.read_csv("src/dataset/brute/Nigerian_Fraud.csv", encoding="latin1")
df5 = pd.read_csv("src/dataset/brute/PhishingEmailData.csv", encoding="latin1")


# Ajouter la colonne target
df1["target"] = 0   # CEAS_08 = légitime
df2["target"] = 0   # Enron = légitime
df3["target"] = 1   # Nazario = phishing
df4["target"] = 1   # Nigerian_Fraud = phishing

# Pour PhishingEmailData, si la colonne existe déjà, on la renomme
if "Label" in df5.columns:
    df5 = df5.rename(columns={"Label": "target"})
else:
    df5["target"] = 1   # si pas de label, on considère phishing
    
# Fusionner verticalement (concaténer les lignes)
merged = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

# Sauvegarder dans un seul fichier CSV
merged.to_csv("src/dataset/merged_dataset.csv", index=False)


# compter le nbre de emails légitimes et de phishing
print(merged["target"].value_counts())

# desequibrage de classes donc il faut la balance des classes
#plus d'email legitime que de phishing, on va utiliser SMOTE pour équilibrer les classes

# Exemple avec la colonne "body"
X = merged["body"].fillna("").astype(str)
y = merged["target"]

# Vectoriser le texte 
# transformer le texte brut en représentations numériques exploitables par le modèle

vectorizer = CountVectorizer(max_features=5000)
X_vec = vectorizer.fit_transform(X)

# Appliquer SMOTE
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_vec, y)

print(pd.Series(y_res).value_counts())

# target equilibré après SMOTE
#0    68921
#1    68921