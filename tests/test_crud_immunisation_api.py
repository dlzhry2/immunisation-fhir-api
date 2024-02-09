import copy
import json
import os
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
    imms["identifier"][0]["value"] = str(uuid.uuid4())

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

    # UPDATE
    new_imms = copy.deepcopy(imms)
    new_imms["id"] = imms_id
    new_imms["status"] = "not-done"
    result = imms_api.update_immunization(imms_id, new_imms)

    assert result.status_code == 200

    # read it back
    result = imms_api.get_immunization_by_id(imms_id)
    res_body = result.json()
    assert res_body["status"] == "not-done"

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
def test_create_immunization_with_stored_identifier_returns_error(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """create should fail if the identifier in the record is not unique"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    identifier = str(uuid.uuid4())

    imms = create_an_imms_obj()
    imms["identifier"][0]["value"] = identifier

    # CREATE IMMUNIZATION
    create_response = imms_api.create_immunization(imms)
    create_res_body = create_response.json()
    create_imms_id = create_res_body["id"]

    assert create_response.status_code == 201
    assert create_res_body["resourceType"] == "Immunization"
    
    # CREATE IMMUNIZATION WITH SAME IDENTIFIER
    failed_create_response = imms_api.create_immunization(imms)
    failed_create_res_body = failed_create_response.json()

    assert failed_create_response.status_code == 500
    assert failed_create_res_body["resourceType"] == "OperationOutcome"

    # DELETE
    delete_response = imms_api.delete_immunization(create_imms_id)
    assert delete_response.status_code == 200


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_update_immunization_with_stored_identifier_returns_error(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """update should fail if the identifier in the record is not unique"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    identifier = str(uuid.uuid4())

    imms = create_an_imms_obj()
    imms["identifier"][0]["value"] = identifier
    
    imms_2 = create_an_imms_obj()
    imms_2["identifier"][0]["value"] = str(uuid.uuid4())

    # CREATE FIRST IMMUNIZATION
    imms_response = imms_api.create_immunization(imms)
    imms_res_body = imms_response.json()
    imms_id = imms_res_body["id"]

    assert imms_response.status_code == 201
    assert imms_res_body["resourceType"] == "Immunization"
    
    # CREATE SECOND IMMUNIZATION
    imms_2_response = imms_api.create_immunization(imms_2)
    imms_2_res_body = imms_2_response.json()
    imms_2_id = imms_2_res_body["id"]

    assert imms_2_response.status_code == 201
    assert imms_2_res_body["resourceType"] == "Immunization"
    
    # UPDATE SECOND IMMUNIZATION WITH FIRST IMMUNIZATIONS IDENTIFIER
    new_imms = copy.deepcopy(imms)
    new_imms["id"] = imms_2_id
    new_imms["status"] = "not-done"
    new_imms["identifier"][0]["value"] = identifier
    update_response = imms_api.update_immunization(imms_2_id, new_imms)
    res_body = update_response.json()

    assert update_response.status_code == 500
    assert res_body["resourceType"] == "OperationOutcome"

    # DELETE BOTH IMMUNIZATIONS
    delete_imms_response = imms_api.delete_immunization(imms_id)
    assert delete_imms_response.status_code == 200
    delete_imms_2_response = imms_api.delete_immunization(imms_2_id)
    assert delete_imms_2_response.status_code == 200


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
def test_update_none_existing_record_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """update a record that doesn't exist should create a new record"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms_id = str(uuid.uuid4())
    imms = create_an_imms_obj(imms_id)
    result = imms_api.update_immunization(imms_id, imms)
    assert result.status_code == 201


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_update_inconsistent_id_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """update should fail if id in the path doesn't match with the id in the message"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    msg_id = str(uuid.uuid4())
    imms = create_an_imms_obj(msg_id)

    path_id = str(uuid.uuid4())
    result = imms_api.update_immunization(path_id, imms)
    json = result.json()

    assert result.status_code == 400
    assert json["resourceType"] == "OperationOutcome"
    assert path_id in json["issue"][0]["diagnostics"]


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_update_deleted_imms_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """updating deleted record will undo the delete"""
    # This behaviour is consistent. Getting a deleted record will result in a 404. An update of a non-existent record
    #  should result in creating a new record
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    imms = create_an_imms_obj()

    # first create and then delete
    result = imms_api.create_immunization(imms)
    assert result.status_code == 201

    imms_id = result.json()["id"]
    result = imms_api.delete_immunization(imms_id)
    assert result.status_code == 200

    # When
    imms["id"] = imms_id
    result = imms_api.update_immunization(imms_id, imms)

    # Then
    assert result.status_code == 201


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
@pytest.mark.parametrize("nhs_number,is_restricted", [(valid_nhs_number_with_s_flag, True), (valid_nhs_number1, False)])
def test_get_s_flag_patient(nhsd_apim_proxy_url, nhsd_apim_auth_headers, nhs_number, is_restricted):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    # Act
    # TODO: Replace this with the usual specification example when it is updated.
    current_directory = os.path.dirname(os.path.realpath(__file__))
    with open(f"{current_directory}/../lambda_code/tests/sample_data/sample_immunization_event.json") as f:
        imms_to_create = json.load(f)
    imms_to_create["patient"]["identifier"]["value"] = nhs_number

    created_imms_result = imms_api.create_immunization(imms_to_create)
    if created_imms_result.status_code != 201:
        pprint.pprint(created_imms_result.text)
        assert created_imms_result.status_code == 201
    created_imms = created_imms_result.json()

    retrieved_get_imms_result = imms_api.get_immunization_by_id(created_imms["id"])
    if retrieved_get_imms_result.status_code != 200:
        pprint.pprint(retrieved_get_imms_result.text)
        assert retrieved_get_imms_result.status_code == 200
    retrieved_get_imms = retrieved_get_imms_result.json()

    sample_disease_code = 840539006
    retrieved_search_imms_result = imms_api.search_immunizations(nhs_number, sample_disease_code)
    if retrieved_search_imms_result.status_code != 200:
        pprint.pprint(retrieved_search_imms_result.text)
        assert retrieved_search_imms_result.status_code == 200
    retrieved_search_imms = next(imms for imms in retrieved_search_imms_result.json()["entry"]
                                 if imms["id"] == created_imms["id"])

    all_retrieved_imms = [retrieved_get_imms, retrieved_search_imms]

    imms_api.delete_immunization(created_imms["id"])

    # Assert
    def get_questionnaire_items(imms):
        questionnaire = next(contained for contained in imms["contained"]
                             if contained["questionnaire"] == "Questionnaire/1")
        return questionnaire["item"]

    def assert_is_not_filtered(imms):
        imms_items = get_questionnaire_items(imms)

        for key in ["SiteName", "Consent"]:
            assert key in [item["linkId"] for item in imms_items]

        assert "N2N9I" != next(item for item in imms_items
                               if item["linkId"] == "SiteCode")["answer"][0]["valueCoding"]["code"]
        assert "reportOrigin" in imms
        assert "location" in imms
        assert all(performer["actor"]["identifier"]["value"] != "N2N9I" for performer in imms["performer"])
        assert all(performer["actor"]["identifier"]["system"] != "https://fhir.nhs.uk/Id/ods-organization-code"
                   for performer in imms["performer"])

    def assert_is_filtered(imms):
        imms_items = get_questionnaire_items(imms)

        for key in ["SiteName", "Consent"]:
            assert key not in [item["linkId"] for item in imms_items]

        assert "N2N9I" == next(item for item in imms_items
                               if item["linkId"] == "SiteCode")["answer"][0]["valueCoding"]["code"]
        assert "reportOrigin" not in imms
        assert "location" not in imms
        assert all(performer["actor"]["identifier"]["value"] == "N2N9I" for performer in imms["performer"])
        assert all(performer["actor"]["identifier"]["system"] == "https://fhir.nhs.uk/Id/ods-organization-code"
                   for performer in imms["performer"])

    assert_is_not_filtered(created_imms)
    for retrieved_imms in all_retrieved_imms:
        if is_restricted:
            assert_is_filtered(retrieved_imms)
        else:
            assert_is_not_filtered(retrieved_imms)
