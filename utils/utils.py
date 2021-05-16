import json
import string
import random

from werkzeug.security import generate_password_hash


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def create_user(user_name):
    _users = json.loads(open('users.json').read())

    _password = get_random_string(8)

    _users.update({
        user_name: generate_password_hash(_password)
    })

    with open('users.json', 'w') as f:
        f.write(json.dumps(_users))

    return _password
