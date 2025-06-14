import os
import sys
import pytest

# Allow importing the Flask app from the repository root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_archivio(client):
    response = client.get('/archivio?pwd=admin123')
    assert response.status_code == 200

def test_export(client):
    response = client.get('/admin/export?pwd=admin123')
    assert response.status_code == 200
