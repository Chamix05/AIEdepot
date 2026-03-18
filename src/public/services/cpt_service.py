
from db_connection import get_connection
from flask import redirect, url_for, flash, render_template
import sys
from services import verif_mdp

def creerCpt(mail,nom, pre, password):
    db =  get_connection()
    cursor = db.cursor(dictionary=True)
    print("Je suis dans la fonction")  # Vérifie ce que Flask reçoit
    sys.stdout.flush()
    p=verif_mdp.hash_password(password)
    cursor.execute("INSERT INTO utilisateur (loginU, nom, pre, mdp) VALUES (%s, %s, %s, %s)", (mail, nom, pre, p))
    db.commit() # enregistrer les changements dans la base de données
    
    if cursor.rowcount > 0: # le nombre de lignes affectées par la requête d'insertion  
     return redirect(url_for("login"))
    else:
     return render_template("compte.html",
                               notif_message="Échec de la création du compte",
                               notif_type="error")
     
     

def emailExiste(mail: str) -> bool:
     db =  get_connection()
     cursor = db.cursor(dictionary=True)
     print("Je suis dans la fonction")  # Vérifie ce que Flask reçoit
     sys.stdout.flush()
     cursor.execute("SELECT 1 FROM utilisateur WHERE loginU = %s", (mail,))
     user = cursor.fetchone()

     cursor.close()
     db.close()

     return bool(user);