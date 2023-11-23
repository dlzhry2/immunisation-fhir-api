import copy
import uuid

import pytest
import requests

from .example_loader import load_example


class ImmunisationApi:

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        }

    def get_immunization_by_id(self, event_id):
        return requests.get(f"{self.url}/event/{event_id}", headers=self._update_headers())

    def create_immunization(self, imms):
        return requests.post(f"{self.url}/event", headers=self._update_headers(), json=imms)

    def delete_immunization(self, imms_id):
        return requests.delete(f"{self.url}/event/{imms_id}", headers=self._update_headers())

    def _update_headers(self, headers=None):
        if headers is None:
            headers = {}
        updated = {**self.headers, **{
            "X-Correlation-ID": str(uuid.uuid4()),
            "X-Request-ID": str(uuid.uuid4()),
        }}
        return {**updated, **headers}


def create_an_imms_obj(imms_id: str = str(uuid.uuid4())) -> dict:
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id

    return imms


def create_a_deleted_imms_resource(imms_api: ImmunisationApi) -> dict:
    imms = create_an_imms_obj()

    stored_imms = imms_api.create_immunization(imms).json()
    imms_id = stored_imms["id"]
    res = imms_api.delete_immunization(imms_id)
    assert res.status_code == 200

    return res.json()


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_crud_immunization_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_an_imms_obj()

    # CREATE
    result = imms_api.create_immunization(imms)
    res_body = result.json()

    assert result.status_code == 201
    assert res_body["resourceType"] == "Immunization"

    # READ
    imms_id = res_body["id"]

    result = imms_api.get_immunization_by_id(imms_id)

    assert result.status_code == 200
    assert res_body["id"] == imms_id

    # DELETE
    result = imms_api.delete_immunization(imms_id)

    assert result.status_code == 200


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_event_by_id_not_found_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    # Act
    result = imms_api.get_immunization_by_id("some-id-that-does-not-exist")
    res_body = result.json()

    # Assert
    assert result.status_code == 404
    assert res_body["resourceType"] == "OperationOutcome"


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_event_by_id_invalid_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    # Act
    result = imms_api.get_immunization_by_id("some_id_that_is_malformed")
    res_body = result.json()

    # Assert
    assert result.status_code == 400
    assert res_body["resourceType"] == "OperationOutcome"


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_delete_immunization_already_deleted(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_a_deleted_imms_resource(imms_api)
    imms_id = imms["id"]

    # Act
    result = imms_api.delete_immunization(imms_id)
    json_result = result.json()

    # Assert
    assert result.status_code == 404
    assert json_result["resourceType"] == "OperationOutcome"


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_deleted_immunization(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_a_deleted_imms_resource(imms_api)
    imms_id = imms["id"]

    # Act
    result = imms_api.get_immunization_by_id(imms_id)
    json_result = result.json()

    # Assert
    assert result.status_code == 404
    assert json_result["resourceType"] == "OperationOutcome"
