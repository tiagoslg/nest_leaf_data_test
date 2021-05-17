import base64
import tempfile
import json

import pytest

from app import app
from utils.utils import create_user
from nest import create_nest


@pytest.fixture
def client():
    user_name = 'test'

    user_file = tempfile.NamedTemporaryFile(mode="w+")
    user_file.write(json.dumps({}))
    user_file.flush()

    password = create_user(user_name, user_file.name)

    app.config['USER_NAME'] = user_name
    app.config['TESTING'] = True
    app.config['PASSWORD'] = password
    app.config['USER_FILE'] = user_file.name

    with app.test_client() as client:
        yield client


def test_auth_requirement(client):
    """Test endpoints that need auth."""

    rv = client.post('/process-default-sample')
    assert rv.status_code == 401

    rv = client.post('/process-json')
    assert rv.status_code == 401


def test_user_creation(client):
    user_name = 'test_2'

    rv = client.post('/create-user')

    assert rv.status_code == 412
    payload = rv.get_json(force=True, silent=True) or {}
    assert 'error' in payload
    assert 'user' in payload['error']

    rv = client.post('/create-user', json={'user_name': user_name})

    assert rv.status_code == 200

    payload = rv.get_json(silent=True, force=True) or {}

    assert payload.get('user_name') == user_name
    assert payload.get('password') is not None


def test_keys_payload_requirements(client):
    """Test app payload required"""
    basic_auth_str = f"{client.application.config['USER_NAME']}:{client.application.config['PASSWORD']}"
    headers = {
        'Authorization': f"Basic " + base64.b64encode(bytes(basic_auth_str, 'ascii')).decode('ascii')
    }

    rv = client.post('/process-default-sample', headers=headers)
    assert rv.status_code == 412
    payload = rv.get_json(force=True, silent=True) or {}
    assert 'error' in payload
    assert 'keys' in payload['error']

    rv = client.post('/process-json', headers=headers)
    assert rv.status_code == 412
    payload = rv.get_json(force=True, silent=True) or {}
    assert 'error' in payload
    assert 'keys' in payload['error']


def test_data_payload_requirements(client):

    basic_auth_str = f"{client.application.config['USER_NAME']}:{client.application.config['PASSWORD']}"
    headers = {
        'Authorization': f"Basic " + base64.b64encode(bytes(basic_auth_str, 'ascii')).decode('ascii')
    }
    keys = ['currency']

    rv = client.post('/process-json', headers=headers, json={'keys': keys})
    assert rv.status_code == 412
    payload = rv.get_json(force=True, silent=True) or {}
    assert 'error' in payload
    assert 'data' in payload['error']


def test_default_sample(client):
    basic_auth_str = f"{client.application.config['USER_NAME']}:{client.application.config['PASSWORD']}"
    headers = {
        'Authorization': f"Basic " + base64.b64encode(bytes(basic_auth_str, 'ascii')).decode('ascii')
    }
    keys = ['currency', 'country', 'city']

    rv = client.post('/process-default-sample', headers=headers, json={'keys': keys})

    assert rv.status_code == 200

    sample_data = json.loads(open('sample.json').read())

    check = create_nest(sample_data, keys)

    payload = rv.get_json(silent=True, force=True) or {}

    assert payload == check


def test_process_json(client):
    basic_auth_str = f"{client.application.config['USER_NAME']}:{client.application.config['PASSWORD']}"
    headers = {
        'Authorization': f"Basic " + base64.b64encode(bytes(basic_auth_str, 'ascii')).decode('ascii')
    }
    keys = ['currency', 'country', 'city']
    sample_data = json.loads(open('sample.json').read())

    rv = client.post('/process-default-sample', headers=headers, json={'keys': keys, 'data': sample_data})

    assert rv.status_code == 200

    check = create_nest(sample_data, keys)

    payload = rv.get_json(silent=True, force=True) or {}

    assert payload == check
