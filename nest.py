import collections.abc
import sys
import json


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            if type(d.get(k)) is list:
                d[k].extend(v)
            elif type(v) is list and len(v) > 0 and not v[0]:
                d[k] = []
            else:
                d[k] = v
    return d


def get_as_list(keys, obj_):

    d = {}

    i = 0
    for key in reversed(keys):
        if key in obj_:
            key_value = obj_.pop(key)

            if i == 0:
                d = {key_value: [obj_]}
            else:
                d = {key_value: d}

            i += 1

    return d


def create_nest(sample, args):

    data_ret = {}

    for data_ in sample:
        dict_update(data_ret, get_as_list(args, data_))

    return data_ret


if __name__ == '__main__':

    if len(sys.argv) <= 1 or not sys.argv[1]:
        sys.stderr.write("ERROR: Missing required nesting levels\n")
        exit(1)

    json_request = ''
    for line in sys.stdin:
        if line:
            json_request += line

    try:
        json_request = json.loads(json_request)
    except json.JSONDecodeError:
        sys.stderr.write("ERROR: Invalid input file\n")
        exit(1)

    ret = create_nest(json_request, sys.argv[1:])

    sys.stdout.write(json.dumps(ret))
