import copy
import json
import os
import random
import uuid
from datetime import datetime

PATIENT_POOL = [
    {"nhs_number": "9999999999", "dob": "1952-05-06"},
    {"nhs_number": "1111111111", "dob": "1987-02-23"},
    {"nhs_number": "1212233445", "dob": "1990-11-15"},
]
SUPPLIER = [
    "https://supplierABC/ODSCode145", "https://supplierSDF/ODSCode123", "https://supplierXYZ/ODSCode735"
]
DISEASE_TYPE = ["covid", "flu", "mmr", "hpv", "polio"]
VACCINE_CODE = ["covidVaccine", "fluVaccine", "mmrVaccine", "hpvVaccine", "polioVaccine"]
VACCINE_PROCEDURE = ["vac_procedure-oral", "vac_procedure-injection", "vac_procedure-123"]
LOCAL_PATIENT_POOL = [
    {"code": "ACME-Patient12345", "system": "https://supplierABC/identifiers/patient"},
    {"code": "ACME-Patient23455", "system": "https://supplierCSB/identifiers/patient"},
    {"code": "ACME-Patient35623", "system": "https://supplierXYZ/identifiers/patient"},
]
ACTION_FLAG = ["flagA", "flagB"]


def generate(num):
    with open("sample_event.json", "r") as template:
        imms = json.loads(template.read())

    _events = []

    def pick_rand(pool):
        idx = random.randint(0, len(pool) - 1)
        return pool[idx]

    for event in range(num):
        _imms = copy.deepcopy(imms)
        # ID
        _imms["identifier"][0]["system"] = pick_rand(SUPPLIER)
        _imms["identifier"][0]["value"] = str(uuid.uuid4())
        # Patient
        patient = pick_rand(PATIENT_POOL)
        _imms["patient"]["identifier"][0]["value"] = patient["nhs_number"]
        _imms["patient"]["birthDate"] = patient["dob"]
        # LocalPatient
        local_pat = pick_rand(LOCAL_PATIENT_POOL)
        _imms["contained"][0]["item"][3]["answer"][0]["valueCoding"]["code"] = local_pat["code"]
        _imms["contained"][0]["item"][3]["answer"][0]["valueCoding"]["system"] = local_pat["system"]
        # Vaccination
        _imms["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"] = pick_rand(DISEASE_TYPE)
        _imms["vaccineCode"]["coding"][0]["code"] = pick_rand(VACCINE_CODE)
        _imms["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = pick_rand(VACCINE_PROCEDURE)

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
    events = generate(30)
    write(events)
