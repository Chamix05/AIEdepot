from copyreg import pickle
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC     
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

#Pour la détection de phishing, on considère phishing = classe positive

bdd = pd.read_csv("src/dataset/processed/dataset_pretraite_vect.csv")

print(bdd.head())
print(bdd.shape)

#cible
y = bdd["target"]

#features
x = bdd.drop(columns="target")

# Initialiser les modèles

#foret= RandomForestClassifier(n_estimators=50, random_state=42,max_depth=10)
bayes = MultinomialNB()
#svm = LinearSVC(max_iter=2000,random_state=42,dual=False)
#log = LogisticRegression(max_iter=1000, random_state=42, solver="saga")

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

#foret.fit(x_train, y_train)
bayes.fit(x_train, y_train)
#svm.fit(x_train, y_train)
#log.fit(x_train, y_train)

# Accuracy : Accuracy (exactitude) = proportion de tous les tuples (emails) correctement classifiés (légitimes + phishing).


# Naive Bayes
y_pred_bayes = bayes.predict(x_test)
print("Naive Bayes")
print(confusion_matrix(y_test, y_pred_bayes))
print(classification_report(y_test, y_pred_bayes))


#choix final:  Naive Bayes

# Sauvegarder le modèle choisi

#model_path = os.path.join(os.path.dirname(__file__), "..", "models", "naive_bayes.pkl")
#with open(model_path, "rb") as f:
    #model = pickle.load(f)

#model_path = os.path.join(os.path.dirname(__file__), "..", "models", "naive_bayes.pkl")

joblib.dump(bayes, "src/models/naive_bayes.pkl")
print("Modèle sauvegardé")
print("Shape attendu par le modèle:", bayes.n_features_in_)
