import copy
import json
import os
import random
import uuid
from datetime import datetime

PATIENT_POOL = [
    {"nhs_number": "9999999999", "dob": "1952-05-06"},
    {"nhs_number": "1111111111", "dob": "1987-02-23"},
]


def generate(num=10):
    with open("sample_event.json", "r") as template:
        imms = json.loads(template.read())

    _events = []

    def pick_rand_patient():
        nhs_index = random.randint(0, len(PATIENT_POOL) - 1)
        return PATIENT_POOL[nhs_index]

    for event in range(num):
        _imms = copy.deepcopy(imms)
        _imms["identifier"][0]["value"] = str(uuid.uuid4())
        patient = pick_rand_patient()
        _imms["patient"]["identifier"][0]["value"] = patient["nhs_number"]
        _imms["patient"]["birthDate"] = patient["dob"]

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
