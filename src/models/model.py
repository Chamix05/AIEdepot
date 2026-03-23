import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC     
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

#Pour la détection de phishing, on considère phishing = classe positive

bdd = pd.read_csv("C:/Users/DELL/Documents/Phishing_PRJ-copie/src/dataset/processed/dataset_pretraite_vect.csv")

print(bdd.head())

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

#test_score_foret = foret.score(x_test, y_test)
#test_score_bayes = bayes.score(x_test, y_test)
#test_score_svm = svm.score(x_test, y_test)
#test_score_log = log.score(x_test, y_test)


# Accuracy : Accuracy (exactitude) = proportion de tous les tuples (emails) correctement classifiés (légitimes + phishing).


#print(f"Random Forest - Test Accuracy: {test_score_foret:.2f}")
#print(f"Naive Bayes - Test Accuracy: {test_score_bayes:.2f}")
#print(f"SVM - Test Accuracy: {test_score_svm:.2f}")
#print(f"Logistic Regression - Test Accuracy: {test_score_log:.2f}")


# Random Forest
#y_pred_foret = foret.predict(x_test)
#print("Random Forest")
#print(confusion_matrix(y_test, y_pred_foret))
#print(classification_report(y_test, y_pred_foret))

# Naive Bayes
y_pred_bayes = bayes.predict(x_test)
print("Naive Bayes")
print(confusion_matrix(y_test, y_pred_bayes))
print(classification_report(y_test, y_pred_bayes))


#choix final:  Naive Bayes

# Sauvegarder le modèle choisi
joblib.dump(bayes, r"C:\\Users\DELL\Documents\\Phishing_PRJ-c2\src\\models\\naive_bayes.pkl")
