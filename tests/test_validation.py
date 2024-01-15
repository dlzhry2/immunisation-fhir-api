import copy

import pytest

from .configuration.config import valid_nhs_number1
from .example_loader import load_example
from .immunisation_api import ImmunisationApi


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
@pytest.mark.debug
def test_coarse_validation(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["patient"]["identifier"]["value"] = valid_nhs_number1
    imms["occurrenceDateTime"] = "2020-12-14"

    response = imms_api.create_immunization(imms)

    assert response.status_code == 400
    assert response.json()["resourceType"] == "OperationOutcome"
