import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_api_items(client):
    resp = client.get('/api/items')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_api_single_item(client):
    # Use an ID known to exist in sample data
    resp = client.get('/api/items/BF001')
    assert resp.status_code == 200


def test_api_item_not_found(client):
    resp = client.get('/api/items/UNKNOWN')
    assert resp.status_code == 404
