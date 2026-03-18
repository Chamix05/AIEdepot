from ast import pattern
import re,time
from services import verif_mdp
from flask import redirect, render_template,request, session, url_for, flash
from services import authen_service
from services import cpt_service
from services import authen_user_service, authen_service,login_admin
import os
uploaded_files = []  # liste en mémoire pour stocker les fichiers importés (un seul à la fois)
def init_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html", files=uploaded_files)

    @app.route("/compte", methods=["GET", "POST"])
    def compte():
        if request.method == "POST":
            nom = request.form.get("nom").strip().lower()
            pre = request.form.get("pre").strip().lower()  # Supprimer les espaces avant/après
            mail = f"{pre}.{nom}@gmail.com"
            password = request.form.get("pass")
            
            if not nom or not pre  or not password:
                
             return render_template("compte.html",
                                   notif_message="Veuillez remplir tous les champs!",
                                   notif_type="warning")
             
            # Vérifier format email
           
            #if not re.fullmatch(rf"{pre}\.{nom}@gmail\.com", mail):
             #return render_template("compte.html",
                                 #  notif_message="Email doit être sous la forme prenom.nom@gmail.com",
                                  # notif_type="warning")
            
                    # Vérifier la longueur minimale du mot de passe
            if len(password) < 6:  # par exemple 6 caractères minimum
             return render_template("compte.html",
                                   notif_message="Le mot de passe doit contenir au moins 6 caractères!",
                                   notif_type="warning")
              # Vérifier mélange lettres + chiffres
            if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
             return render_template("compte.html",
                                   notif_message="Le mot de passe doit contenir des lettres ET des chiffres!",
                                   notif_type="warning")
             
                # Vérifier si l'email existe déjà
            if cpt_service.emailExiste(mail):
               return render_template("compte.html",
                                   notif_message="Cet email existe déjà, veuillez en choisir un autre!",
                                   notif_type="warning")
             
            return cpt_service.creerCpt(mail, nom, pre, password)
        
            
            
        
         #Quand tu arrives sur /compte → c’est une requête GET → Flask doit renvoyer la page HTML avec le formulaire (render_template("compte.html")).
        return render_template("compte.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "attempts" not in session:
         session["attempts"] = 0
        if "lock_until" not in session:
         session["lock_until"] = 0

     # Vérifier si l’utilisateur est bloqué
        if time.time() < session["lock_until"]:
         return render_template("login.html",
                               notif_message="Trop de tentatives. Réessayez dans quelques minutes.",
                               notif_type="error")
        if request.method == "POST":
            username = request.form.get("mail")
            password = request.form.get("pass")
            
            if not username or not password:
             return render_template("login.html",
                                   notif_message="Veuillez remplir tous les champs!",
                                   notif_type="warning")

             
             # Tentative échouée → incrémenter compteur
             # Authentification
            if username.endswith("@gmail.com") and "john.doe" in username:
               return login_admin.check_login(username,password,"$argon2id$v=19$m=65536,t=3,p=4$1/qfk/L+n7M2pjRGiBFCqA$fusioJnuLiHvmxgW7Y0qBRDjlhzvTzX7n8EGKtJ9DpE")
            
            result =authen_user_service.authenticate(username, password)
                
            if not result:  # si échec
                   session["attempts"] += 1
                   if session["attempts"] >= 3:
                     session["lock_until"] = time.time() + 60  # bloquer 60s
                     session["attempts"] = 0
                     return render_template("login.html",
                                           notif_message="3 tentatives échouées. Réessayez dans 1 minute.",
                                           notif_type="error")
                   else:
                        return render_template("login.html",
                                           notif_message=f"Identifiants incorrects. Tentative {session['attempts']} sur 3.",
                                           notif_type="error")
            else:
                 # succès → reset compteur
                  session["attempts"] = 0
                  return redirect(url_for("dashboard"))
                         
        return render_template("login.html")
    
    @app.route("/logout")
    def logout():
       # Supprimer toutes les données de session
        session.clear()
        return redirect(url_for("login"))     
    
    @app.route("/about")
    def about():
        return render_template("about.html") 
    
    @app.route("/upload", methods=["POST"])
    def upload():
        print("UPLOAD ROUTE CALLED")
        notif_message = None
        notif_type = None
        
        file = request.files.get("file")
        print("DEBUG file object:", file)
        print("DEBUG filename:", repr(file.filename))
        # Cas 1 : champ absent ou fichier non choisi
        if not file or not file.filename or file.filename.strip() == "":
         notif_message = "Veuillez choisir un fichier"
         notif_type = "error"
         print("DEBUG: Aucun fichier choisi")
         return render_template("dashboard.html", files=uploaded_files,
                               notif_message=notif_message, notif_type=notif_type)

        if not file.filename.lower().endswith(".eml"):
            notif_message = "Seuls les fichiers .eml sont autorisés"
            notif_type = "error"
            return render_template("dashboard.html", files=uploaded_files,
                                   notif_message=notif_message, notif_type=notif_type)

        # Sauvegarde
        filepath = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)

        # Remplacer la liste par un seul fichier (un seul à la fois)
        uploaded_files.clear()
        uploaded_files.append(file.filename)

        notif_message = "Fichier importé avec succès"
        notif_type = "success"

        return render_template("dashboard.html", files=uploaded_files,
                               notif_message=notif_message, notif_type=notif_type)