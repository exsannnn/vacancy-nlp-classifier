import pytest
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_api_search_no_query(client):
    rv = client.get('/api/search')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'results' in json_data

def test_api_stats(client):
    rv = client.get('/api/stats')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'total' in json_data
    assert 'active' in json_data
    assert 'avgQuality' in json_data
    assert isinstance(json_data['total'], int)
    assert isinstance(json_data['active'], int)
    assert isinstance(json_data['avgQuality'], (int, float))

def test_api_categories(client):
    rv = client.get('/api/categories')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'categories' in json_data
    assert isinstance(json_data['categories'], list)

def test_api_levels(client):
    rv = client.get('/api/levels')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'levels' in json_data
    assert isinstance(json_data['levels'], list)