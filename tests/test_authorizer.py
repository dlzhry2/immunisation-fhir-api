import copy
import uuid

import pytest

from .configuration.config import valid_nhs_number1
from .example_loader import load_example
from .immunisation_api import ImmunisationApi, parse_location


def create_an_imms_obj(imms_id: str = str(uuid.uuid4()), nhs_number=valid_nhs_number1) -> dict:
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["patient"]["identifier"]["value"] = nhs_number

    return imms


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
@pytest.mark.debug
def test_crud_immunization_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_an_imms_obj()

    # CREATE
    result = imms_api.create_immunization(imms)

    assert result.text == ""
    assert result.status_code == 201
    assert "Location" in result.headers

    # READ
    imms_id = parse_location(result.headers["Location"])

    result = imms_api.get_immunization_by_id(imms_id)
    res_body = result.json()

    assert result.status_code == 200
    assert res_body["id"] == imms_id
