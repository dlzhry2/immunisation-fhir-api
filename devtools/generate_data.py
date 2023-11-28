import copy
import json
import os
import random
import uuid
from datetime import datetime

# generate reproducible random UUIDs
rd = random.Random()
rd.seed(0)


def make_rand_id():
    return uuid.UUID(int=rd.getrandbits(128))


patient_pool = [
    {"nhs_number": "9999999999"},
    {"nhs_number": "1111111111"},
    {"nhs_number": "1212233445"},
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
        _imms["id"] = str(make_rand_id())
        _imms["identifier"][0]["system"] = pick_rand(suppliers)
        _imms["identifier"][0]["value"] = str(make_rand_id())

        # Patient
        patient = pick_rand(patient_pool)
        _imms["patient"]["identifier"]["value"] = patient["nhs_number"]
        # Vaccination
        _imms["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"] = pick_rand(disease_type)
        _imms["vaccineCode"]["coding"][0]["code"] = pick_rand(vaccine_code)
        # _imms["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = pick_rand(vaccine_procedure)
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
