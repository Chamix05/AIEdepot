from flask import Flask
import db_connection    
from routes import routes   

app = Flask(__name__,template_folder="templates", static_folder="static")

app.secret_key = "ma_cle_ultra_secrete_et_unique" # necessaire pour que les messages flash fonctionnent

if db_connection.get_connection().is_connected():
    print("Connexion MySQL réussie")
else:
    print("Échec de la connexion")

# Enregistrer les routes définies dans routes.py
routes.init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
