import copy
import json
import os
import random
import uuid
from datetime import datetime

# we want to generate random UUIDs but, we want to make them reproducible
# see: https://stackoverflow.com/a/56757552/3943054
rd = random.Random()
rd.seed(0)
uuid.uuid4 = lambda: uuid.UUID(int=rd.getrandbits(128))

patient_pool = [
    {"nhs_number": "9999999999", "dob": "1952-05-06"},
    {"nhs_number": "1111111111", "dob": "1987-02-23"},
    {"nhs_number": "1212233445", "dob": "1990-11-15"},
]
suppliers = [
    "https://supplierABC/ODSCode145", "https://supplierSDF/ODSCode123", "https://supplierXYZ/ODSCode735"
]
disease_type = ["covid", "flu", "mmr", "hpv", "polio"]
vaccine_code = ["covidVaccine", "fluVaccine", "mmrVaccine", "hpvVaccine", "polioVaccine"]
vaccine_procedure = ["vac_procedure-oral", "vac_procedure-injection", "vac_procedure-123"]
local_patient_pool = [
    {"code": "ACME-Patient12345", "system": "https://supplierABC/identifiers/patient"},
    {"code": "ACME-Patient23455", "system": "https://supplierCSB/identifiers/patient"},
    {"code": "ACME-Patient35623", "system": "https://supplierXYZ/identifiers/patient"},
]
action_flag = ["flagA", "flagB"]


def pick_rand(pool):
    idx = random.randint(0, len(pool) - 1)
    return pool[idx]


def generate_immunisation(num):
    with open("sample_imms.json", "r") as template:
        imms = json.loads(template.read())

    all_imms = []
    for _ in range(num):
        _imms = copy.deepcopy(imms)
        # ID
        _imms["id"] = str(uuid.uuid4())
        _imms["identifier"][0]["system"] = pick_rand(suppliers)
        _imms["identifier"][0]["value"] = str(uuid.uuid4())

        all_imms.append(_imms)

    return all_imms


def write(_data, resource_type):
    path = "sample_data"
    if not os.path.exists(path):
        os.makedirs(path)

    name = f"{datetime.today().strftime('%Y-%m-%dT%H:%M:%S')}_{resource_type}-{len(_data)}.json"
    with open(f"{path}/{name}", "w") as sample_file:
        json_events = json.dumps(_data, indent=2)
        sample_file.write(json_events)


if __name__ == '__main__':
    imms = generate_immunisation(30)
    write(imms, resource_type="immunisation")
