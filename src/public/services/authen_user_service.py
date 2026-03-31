
from ..db_connection import get_connection
from flask import redirect, url_for, render_template
import sys
from ..services import verif_mdp

def authenticate(username, password):
    db =  get_connection()
    cursor = db.cursor(dictionary=True)
    print("DEBUG:", username, password)  # Vérifie ce que Flask reçoit
    print("Je suis dans la fonction")  # Vérifie ce que Flask reçoit
    sys.stdout.flush()
    cursor.execute("SELECT * FROM utilisateur WHERE loginU=%s", (username,))
    user = cursor.fetchone()

    cursor.close()
    db.close()
    
    if user and verif_mdp.check_password(password, user["mdp"]):
        # Mot de passe correct
        return True
    else:
        # Mot de passe incorrect ou utilisateur inexistant
        return False

   
    
      
