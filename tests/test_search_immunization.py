import copy
import uuid

import pytest

from .example_loader import load_example
from .test_crud_immunisation_api import ImmunisationApi


def create_immunization(imms_id, nhs_number, disease_code):
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["patient"]["identifier"]["value"] = nhs_number
    imms["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"] = disease_code

    return imms


def seed_search_records(imms_api: ImmunisationApi):
    flu_code = "flue-code-1234"
    mmr_code = "mmr-code-2345"
    # create one patient with two diseases
    patient1 = "2345564537"
    p1_flu = create_immunization(patient1, str(uuid.uuid4()), flu_code)
    p2_mmr = create_immunization(patient1, str(uuid.uuid4()), mmr_code)

    all_imms = []
    imms1 = imms_api.create_immunization(p1_flu)
    imms2 = imms_api.create_immunization(p2_mmr)

    all_imms.append(imms1.json())
    all_imms.append(imms2.json())

    return all_imms


def cleanup(imms_api: ImmunisationApi, all_imms: list):
    print("Removing all imms")
    for imms in all_imms:
        imms_api.delete_immunization(imms["id"])


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
@pytest.mark.debug
def test_search_immunization(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    stored_imms = seed_search_records(imms_api)

    cleanup(imms_api, stored_imms)
