import copy
import uuid
from time import sleep

import pytest

from .example_loader import load_example
from .test_crud_immunisation_api import ImmunisationApi


def create_immunization(imms_id, nhs_number, disease_code):
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["patient"]["identifier"]["value"] = nhs_number
    imms["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"] = disease_code

    return imms


flu_code = "flue-code-1234"
mmr_code = "mmr-code-2345"
scenarios = [
    {
        "nhs_number": "2345564537",
        "diseases": [flu_code, mmr_code],
        "responses": [],
    }
]


def seed_search_records(imms_api: ImmunisationApi):
    _scenarios = copy.deepcopy(scenarios)
    for scenario in _scenarios:
        nhs_number = scenario["nhs_number"]
        for disease in scenario["diseases"]:
            imms = create_immunization(str(uuid.uuid4()), nhs_number, disease)

            stored_imms = imms_api.create_immunization(imms)
            if stored_imms.status_code != 201:
                print(stored_imms.json())
            assert stored_imms.status_code == 201
            sleep(0.1)

            scenario["responses"].append(stored_imms.json())

    return _scenarios


def cleanup(imms_api: ImmunisationApi, processed_scenarios: list):
    for scenario in processed_scenarios:
        for imms in scenario["responses"]:
            delete_res = imms_api.delete_immunization(imms["id"])
            if delete_res.status_code != 200:
                print(delete_res.json())
            assert delete_res.status_code == 200
            sleep(0.1)


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
    imms_api = ImmunisationApi("https://internal-dev.api.service.nhs.uk/immunisation-fhir-api-pr-56", token)

    _scenarios = seed_search_records(imms_api)

    # Tests
    # Search patient with multiple disease types
    scenario = _scenarios[0]
    response = imms_api.search_immunizations(scenario["nhs_number"], mmr_code)

    results = response.json()
    print(results)
    assert response.status_code == 200
    assert results["resourceType"] == "List"

    # Cleanup
    cleanup(imms_api, _scenarios)
