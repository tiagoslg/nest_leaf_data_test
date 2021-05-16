import json

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from utils import get_random_string
from nest import create_nest

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    users = json.loads(open('users.json').read())
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/process-json', methods=['POST'])
@auth.login_required
def process_json():
    _payload = request.get_json(silent=True, force=True) or {}

    assert 'keys' in _payload, "Missing keys information"
    assert 'data' in _payload, "Missing data information"

    _keys = _payload['keys']
    _data = _payload['data']

    assert type(_keys) is list
    assert type(_data) is list

    return create_nest(_data, _keys)


@app.route("/create-user", methods=['POST'])
def create_user():
    _payload = request.get_json(silent=True, force=True) or {}

    assert 'user_name' in _payload, "Missing username data"

    _users = json.loads(open('users.json').read())

    _user_name = _payload.get('user_name')

    assert _user_name not in _users, "Username already exists"

    _password = get_random_string(8)

    _users.update({
        _user_name: generate_password_hash(_password)
    })

    with open('users.json', 'w') as f:
        f.write(json.dumps(_users))

    return {"user_name": _user_name, "password": _password}


if __name__ == '__main__':
    app.run()