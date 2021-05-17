import json
import string
import random

from werkzeug.security import generate_password_hash


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    result_str = ''.join(random.choice(letters) for _ in range(length))

    return result_str


def create_user(user_name, user_file):
    _users = json.loads(open(user_file).read())

    _password = get_random_string(8)

    _users.update({
        user_name: generate_password_hash(_password)
    })

    with open(user_file, 'w') as f:
        f.write(json.dumps(_users))

    return _password
