import copy
import json
import os
import uuid

from .constants import valid_nhs_number1

current_directory = os.path.dirname(os.path.realpath(__file__))


def load_example(path: str) -> dict:
    with open(f"{current_directory}/../../specification/components/examples/{path}") as f:
        return json.load(f)


def create_an_imms_obj(imms_id: str = str(uuid.uuid4()),
                       nhs_number=valid_nhs_number1,
                       disease_code=None) -> dict:
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["contained"][1]["identifier"][0]["value"] = nhs_number
    if disease_code:
        imms["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = disease_code

    return imms


def get_questionnaire_items(imms):
    questionnaire = next(
        contained
        for contained in imms["contained"]
        if contained["resourceType"] == "QuestionnaireResponse"
    )
    return questionnaire["item"]
