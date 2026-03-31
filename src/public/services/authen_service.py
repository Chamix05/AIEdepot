
from ..db_connection import get_connection
from flask import redirect, url_for, flash
import sys
from ..services import verif_mdp

def authenticate(username, password):
    db =  get_connection()
    cursor = db.cursor(dictionary=True)
    print("DEBUG:", username, password)  # Vérifie ce que Flask reçoit
    print("Je suis dans la fonction")  # Vérifie ce que Flask reçoit
    sys.stdout.flush()
    cursor.execute("SELECT * FROM administrateur WHERE loginA=%s AND mdp=%s", (username, password))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    return bool(user);
