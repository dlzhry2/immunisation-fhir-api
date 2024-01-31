import copy
import pprint
import uuid

import pytest

from .configuration.config import valid_nhs_number1, valid_nhs_number_with_s_flag
from .example_loader import load_example
from .immunisation_api import ImmunisationApi


def create_an_imms_obj(imms_id: str = str(uuid.uuid4()), nhs_number=valid_nhs_number1) -> dict:
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["patient"]["identifier"]["value"] = nhs_number

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
    if result.status_code != 404:
        print(result.text)
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


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_bad_nhs_number_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_an_imms_obj(nhs_number="7463384756")

    # CREATE
    result = imms_api.create_immunization(imms)
    res_body = result.json()

    assert result.status_code == 400
    assert res_body["resourceType"] == "OperationOutcome"


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_s_flag_patient(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    # Act
    imms = create_an_imms_obj(nhs_number=valid_nhs_number_with_s_flag)
    created_imms = imms_api.create_immunization(imms)
    if created_imms.status_code != 201:
        pprint.pprint(created_imms.text)
        raise AssertionError
    created_imms_json = created_imms.json()

    retrieved_imms = imms_api.get_immunization_by_id(created_imms_json["id"])
    if retrieved_imms.status_code != 200:
        pprint.pprint(retrieved_imms.text)
        assert retrieved_imms.status_code == 201
    retrieved_imms_json = retrieved_imms.json()

    imms_api.delete_immunization(created_imms_json["id"])

    # Assert
    def get_questionnaire_item_ids(imms):
        questionnaire = next(contained for contained in imms["contained"]
                             if contained["questionnaire"] == "Questionnaire/1")
        return [item["linkId"] for item in questionnaire["item"]]

    for key in ["SiteCode", "SiteName"]:
        assert key in get_questionnaire_item_ids(created_imms_json)
    for key in ["SiteCode", "SiteName"]:
        assert key not in get_questionnaire_item_ids(retrieved_imms_json)
