import copy
import json
import os
import random
import uuid
from datetime import datetime


def generate(num=10):
    with open("sample_event.json", "r") as template:
        imms = json.loads(template.read())

    _events = []
    nhs_number_pool = ["999999999", "111111111"]

    for event in range(num):
        _imms = copy.deepcopy(imms)
        _imms["identifier"][0]["value"] = str(uuid.uuid4())
        nhs_index = random.randint(0, len(nhs_number_pool) - 1)
        _imms["patient"]["identifier"][0]["value"] = nhs_number_pool[nhs_index]

        _events.append(_imms)

    return _events


def write(_events):
    path = "sample_data"
    if not os.path.exists(path):
        os.makedirs(path)

    name = f"{datetime.today().strftime('%Y-%m-%dT%H:%M:%S')}_{len(_events)}.json"
    with open(f"{path}/{name}", "w") as sample_file:
        json_events = json.dumps(_events, indent=2)
        sample_file.write(json_events)


if __name__ == '__main__':
    events = generate()
    write(events)
