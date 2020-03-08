import json


def read_json(file):
    with open(file, 'r') as f:
        return json.load(f)


def add_data_to_json(file, data):
    param = read_json(file)
    param.append(data)
    with open('file', 'w') as f:
        json.dump(param, f, ensure_ascii=False)