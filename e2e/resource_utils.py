import copy
import json
import os
import uuid

from config import valid_nhs_number1

current_directory = os.path.dirname(os.path.realpath(__file__))


def load_example(path: str) -> dict:
    with open(f"{current_directory}/../specification/components/examples/{path}") as f:
        return json.load(f)


def create_an_imms_obj(
    imms_id: str = str(uuid.uuid4()), nhs_number=valid_nhs_number1
) -> dict:
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["contained"][1]["identifier"][0]["value"] = nhs_number

    return imms
