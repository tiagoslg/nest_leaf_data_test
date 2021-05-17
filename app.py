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

app.config['USER_FILE'] = 'users.json'


@auth.verify_password
def verify_password(username, password):
    user_file = app.config.get('USER_FILE')
    users = json.loads(open(user_file).read())
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/process-json', methods=['POST'])
@auth.login_required
def process_json():
    _payload = request.get_json(silent=True, force=True) or {}

    if 'keys' not in _payload:
        return {'error': "Missing required keys information"}, 412

    if 'data' not in _payload:
        return {'error': "Missing required data information"}, 412

    _keys = _payload['keys']
    _data = _payload['data']

    if type(_keys) is not list:
        return {'error': "Invalid keys type"}, 412

    if type(_data) is not list:
        return {'error': "Invalid data type"}, 412

    return create_nest(_data, _keys)


@app.route('/process-default-sample', methods=['POST'])
@auth.login_required
def process_default_sample():
    _payload = request.get_json(silent=True, force=True) or {}

    if 'keys' not in _payload:
        return {'error': "Missing required keys information"}, 412

    _keys = _payload['keys']

    if type(_keys) is not list:
        return {'error': "Invalid keys type"}, 412

    _data = json.loads(open('sample.json').read())

    return create_nest(_data, _keys)


@app.route("/create-user", methods=['POST'])
def create_user():
    _user_file = app.config.get('USER_FILE')
    _payload = request.get_json(silent=True, force=True) or {}

    if 'user_name' not in _payload:
        return {'error': "Missing required user information"}, 412

    _user_name = _payload.get('user_name')

    _password = json_create_user(_user_name, _user_file)

    return {"user_name": _user_name, "password": _password}


if __name__ == '__main__':
    app.run()
