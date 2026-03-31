import os
from flask import Flask
from . import db_connection  #import db_connection   
from .routes import routes  #from routes import routes     importer le module routes/routes.py

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
#app = Flask(__name__,template_folder="templates", static_folder="static")

app.secret_key = "ma_cle_ultra_secrete_et_unique" # necessaire pour que les messages flash fonctionnent

if db_connection.get_connection().is_connected():
    print("Connexion MySQL réussie")
else:
    print("Échec de la connexion")

# Enregistrer les routes définies dans routes.py
routes.init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
