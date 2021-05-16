import json

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from utils.utils import create_user as json_create_user

from nest import create_nest

app = Flask(__name__)
auth = HTTPBasicAuth()

try:
    open('users.json')
except FileNotFoundError:
    f = open('users.json', 'x')
    f.write(json.dumps({}))
    f.close()


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


@app.route('/process-default-sample', methods=['POST'])
@auth.login_required
def process_default_sample():
    _payload = request.get_json(silent=True, force=True) or {}

    assert 'keys' in _payload, "Missing keys information"

    _keys = _payload['keys']

    assert type(_keys) is list

    _data = json.loads(open('sample.json').read())

    return create_nest(_data, _keys)


@app.route("/create-user", methods=['POST'])
def create_user():
    _payload = request.get_json(silent=True, force=True) or {}

    assert 'user_name' in _payload, "Missing username data"

    _user_name = _payload.get('user_name')

    _password = json_create_user(_user_name)

    return {"user_name": _user_name, "password": _password}


if __name__ == '__main__':
    app.run()