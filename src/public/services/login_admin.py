import time

from flask import redirect, render_template, session, url_for
from ..services import authen_service,verif_mdp

def check_login(username,password,expected_pass):
    
    
    if  verif_mdp.check_password(password, expected_pass):
        session["attempts"] = 0
        return redirect(url_for("dashboard"))
    else:
        result = authen_service.authenticate(username, password)
        if not result:
            session["attempts"] += 1
            if session["attempts"] >= 3:
                session["lock_until"] = time.time() + 60
                session["attempts"] = 0
                return render_template("login.html",
                                       notif_message="3 tentatives échouées. Réessayez dans 1 minute.",
                                       notif_type="error")
            else:
                return render_template("login.html",
                                       notif_message=f"Identifiants incorrects. Tentative {session['attempts']} sur 3.",
                                       notif_type="error")
        else:
           session["attempts"] = 0
           return redirect(url_for("dashboard"))
   
