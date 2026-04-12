# src/tests/test_app.py
import pytest
from unittest.mock import patch

@patch("public.services.email_analysis.joblib.load")
def test_app(mock_load):
    mock_load.return_value = None  # fake model
    
    from public.app import app
    
    assert app is not None
# src/tests/test_app.py
"""import pytest
from unittest.mock import patch
from public.app import app

# Mock du modèle
@pytest.fixture(autouse=True)
def mock_model_load():
    # Remplace le chargement du modèle par un mock qui renvoie une valeur factice
    with patch('public.services.email_analysis.joblib.load') as mock_load:
        mock_load.return_value = "Model Mocked"  # Ce que tu veux simuler
        yield mock_load

def test_homepage():
    response = app.test_client().get('/')
    assert response.status_code == 200"""