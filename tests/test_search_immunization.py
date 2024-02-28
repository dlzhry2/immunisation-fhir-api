import copy
import uuid
from time import sleep
from typing import List, Literal, NamedTuple, Optional

import pytest

from .configuration.config import valid_nhs_number1, valid_nhs_number2
from .example_loader import load_example
from .immunisation_api import ImmunisationApi, parse_location


def create_immunization(imms_id, nhs_number, disease_code):
    imms = copy.deepcopy(load_example("Immunization/POST-Immunization.json"))
    imms["id"] = imms_id
    imms["contained"][1]["identifier"][0]["value"] = nhs_number
    imms["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = disease_code
    imms['identifier'][0]['value'] = str(uuid.uuid4())
    return imms


flu_code = "mockFLUcode1"
mmr_code = "mockMMRcode1"
covid_code = "1324681000000101"


def seed_records(imms_api: ImmunisationApi, records):
    _records = copy.deepcopy(records)
    for record in _records:
        nhs_number = record["nhs_number"]
        for disease in record["diseases"]:
            imms = create_immunization(str(uuid.uuid4()), nhs_number, disease)

            create_res = imms_api.create_immunization(imms)
            assert create_res.status_code == 201
            imms_id = parse_location(create_res.headers["Location"])
            sleep(0.1)
            get_res = imms_api.get_immunization_by_id(imms_id)

            record["responses"].append(get_res.json())

    return _records


def cleanup(imms_api: ImmunisationApi, stored_records: list):
    for record in stored_records:
        for resource in record["responses"]:
            delete_res = imms_api.delete_immunization(resource["id"])
            assert delete_res.status_code == 204
            sleep(0.1)


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_search_immunization(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """it should filter based on disease type"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    records = [
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [mmr_code],
            "responses": [],
        },
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [flu_code],
            "responses": [],
        },
        {
            "nhs_number": valid_nhs_number2,
            "diseases": [flu_code, mmr_code, covid_code, mmr_code],
            "responses": [],
        },
    ]
    stored_records = seed_records(imms_api, records)
    # Tests
    # Search patient with multiple disease types
    response = imms_api.search_immunizations(stored_records[0]["nhs_number"], "MMR")

    cleanup(imms_api, stored_records)

    # Then
    results = response.json()
    result_ids = [result["resource"]["id"] for result in results["entry"]]
    assert response.status_code == 200
    assert results["resourceType"] == "Bundle"
    for resource in stored_records[0]["responses"]:
        assert resource["id"] in result_ids
    for resource in stored_records[1]["responses"]:
        assert resource["id"] not in result_ids


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_search_immunization_ignore_deleted(
    nhsd_apim_proxy_url, nhsd_apim_auth_headers
):
    """it should filter out deleted items"""
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    records = [
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [mmr_code, mmr_code],
            "responses": [],
        },
        {  # same nhs_number but, we will delete it in this test and not during cleanup
            "nhs_number": valid_nhs_number1,
            "diseases": [mmr_code],
            "responses": [],
        },
    ]

    stored_records = seed_records(imms_api, records)

    # Search patient with deleted items
    id_to_delete = stored_records[1]["responses"][0]["id"]
    _ = imms_api.delete_immunization(id_to_delete)

    records = stored_records[0]
    response = imms_api.search_immunizations(records["nhs_number"], "MMR")

    # pop the one that we already deleted
    stored_records.pop()
    cleanup(imms_api, stored_records)

    # Then
    results = response.json()
    result_ids = [result["resource"]["id"] for result in results["entry"]]

    assert response.status_code == 200
    assert results["resourceType"] == "Bundle"
    assert id_to_delete not in result_ids
    for record in stored_records:
        for resource in record["responses"]:
            assert resource["id"] in result_ids


@pytest.mark.debug
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_search_immunization_parameter_locations(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """it should filter based on disease type regardless of if parameters are in the URL or content"""

    # Arrange

    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    records = [
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [mmr_code],
            "responses": [],
        },
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [flu_code],
            "responses": [],
        },
        {
            "nhs_number": valid_nhs_number2,
            "diseases": [flu_code, mmr_code, covid_code, mmr_code],
            "responses": [],
        },
    ]
    stored_records = seed_records(imms_api, records)

    created_resources = [response for resource in stored_records for response in resource["responses"]]
    created_resource_ids = [result["id"] for result in created_resources]

    # Act
    class SearchTestParams(NamedTuple):
        method: Literal["POST", "GET"]
        query_string: str
        body: Optional[str]
        should_be_success: bool
        returned_indexes: List[int]

    searches = \
        [SearchTestParams("GET", f"-patient.identifier={valid_nhs_number1}&-immunization.target=MMR", None, True, [0]),
         SearchTestParams("GET", f"-patient.identifier={valid_nhs_number1}&-immunization.target=MMR&-immunization.target=FLU", None, True, [0, 1]),
         SearchTestParams("GET", f"-patient.identifier={valid_nhs_number1}&-immunization.target=MMR", f"-patient.identifier={valid_nhs_number1}", True, [0]),  # GET does not support body.
         SearchTestParams("POST", f"-patient.identifier={valid_nhs_number1}&-immunization.target=MMR", f"-patient.identifier={valid_nhs_number1}", False, []),
         SearchTestParams("GET", f"-patient.identifier={valid_nhs_number1}&-nhsNumber={valid_nhs_number1}&-immunization.target=MMR", None, False, []),
         SearchTestParams("GET", f"-patient.identifier={valid_nhs_number1}&-immunization.target=MMR,FLU", None, False, [0, 1])] # "and" params not supported.

    try:
        for search in searches:

            pprint.pprint(search)
            response = imms_api.search_immunizations_full(search.method, search.query_string, search.body)

            # Then
            #pprint.pprint(response.text)
            #pdb.set_trace()
            assert response.ok == search.should_be_success

            if search.should_be_success:
                results: dict = response.json()
                assert "entry" in results.keys()
                result_ids = [result["resource"]["id"] for result in results["entry"]]
                assert response.status_code == 200
                assert results["resourceType"] == "Bundle"

                expected_created_resource_ids = \
                    [created_resource_id for i, created_resource_id in enumerate(created_resource_ids)
                     if i in search.returned_indexes]

                for expected_created_resource_id in expected_created_resource_ids:
                    assert expected_created_resource_id in result_ids

                # for resource in created_resources[0]["responses"]:
                #     assert resource["id"] in result_ids
                # for resource in created_resources[1]["responses"]:
                #     assert resource["id"] not in result_ids

    except AssertionError:
        cleanup(imms_api, stored_records)
        raise
