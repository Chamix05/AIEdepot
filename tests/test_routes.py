import pytest
from flask import Flask
import sys, os
from src.public.app import init_routes   # un seul import, cohérent

# Ajouter src/ au chemin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    init_routes(app)
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_compte_get(client):
    response = client.get("/compte")
    assert response.status_code == 200

def test_dashboard(client):
    response = client.get("/dashboard")
    assert response.status_code == 200

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_logout(client):
    response = client.get("/logout")
    # logout redirige vers /login → code 302 (redirect)
    assert response.status_code == 302

def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200

def test_upload_without_file(client):
    response = client.post("/upload", data={})
    # devrait renvoyer la page dashboard avec message d’erreur
    assert response.status_code == 200
    assert b"Veuillez choisir un fichier" in response.data
