import copy
import datetime
import pprint
import uuid
from time import sleep
from typing import List, Literal, NamedTuple, Optional

import pytest

from .configuration.config import valid_nhs_number1, valid_nhs_number2, valid_nhs_number_param1, valid_nhs_number_param2
from .example_loader import load_example
from .immunisation_api import ImmunisationApi, parse_location


def create_immunization(imms_id, nhs_number, disease_code, occurrence_date_time: Optional[str]):
    imms = copy.deepcopy(load_example(f"Immunization/POST-{disease_code}-Immunization.json"))
    imms["id"] = imms_id
    imms["contained"][1]["identifier"][0]["value"] = nhs_number
    imms["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = disease_code
    imms["identifier"][0]["value"] = str(uuid.uuid4())
    if occurrence_date_time is not None:
        imms["occurrenceDateTime"] = occurrence_date_time
    return imms


flu_code = "822851000000102"
mmr_code = "mockMMRcode1"
covid_code = "1324681000000101"


def seed_records(imms_api: ImmunisationApi, records):
    _records = copy.deepcopy(records)
    for record in _records:
        nhs_number = record["nhs_number"]
        occurrence_date_time = record.get("occurrence_date_time", None)
        for disease in record["diseases"]:
            imms = create_immunization(str(uuid.uuid4()), nhs_number, disease, occurrence_date_time)

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
def test_search_immunization_ignore_deleted(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
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


#@pytest.mark.debug
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
            "responses": []
        },
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [flu_code],
            "responses": [],
        },
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [covid_code],
            "responses": [],
            "occurrenceDateTime": "2024-01-30T13:28:17.271+00:00"
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
        expected_indexes: List[int]

    searches = \
        [SearchTestParams("GET", "", None, False, []),
         # No results.
         SearchTestParams("GET", f"patient.identifier={valid_nhs_number_param2}&-immunization.target=MMR",
                          None, True, []),
         SearchTestParams("GET", f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR",
                          None, True, [0]),
         SearchTestParams("GET",
                          f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR,FLU",
                          None, True, [0, 1]),
         # GET does not support body.
         SearchTestParams("GET", f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR",
                          f"patient.identifier={valid_nhs_number_param1}", True, [0]),
         SearchTestParams("POST", "",
                          f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR", True, [0]),
         SearchTestParams("POST", f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR",
                          f"patient.identifier={valid_nhs_number_param1}", False, []),
         SearchTestParams("GET",
                          f"patient.identifier={valid_nhs_number_param1}&patient.identifier={valid_nhs_number_param1}"
                          f"&-immunization.target=MMR",
                          None, False, []),
         # "and" params not supported.
         SearchTestParams("GET",
                          f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR&-immunization.target=FLU",
                          None, False, [0, 1]),
         SearchTestParams("GET",
                          f"patient.identifier={valid_nhs_number_param1}&-immunization.target=COVID19"
                          f"&-date.from=2023-12-31&-date.to=2024-01-31",
                          None, True, [2])]

    try:
        for search in searches:
            pprint.pprint(search)
            response = imms_api.search_immunizations_full(search.method, search.query_string, search.body)

            # Then
            #pprint.pprint(response.text)
            assert response.ok == search.should_be_success, response.text

            results: dict = response.json()
            if search.should_be_success:
                assert "entry" in results.keys()
                result_ids = [result["resource"]["id"] for result in results["entry"]]
                assert response.status_code == 200
                assert results["resourceType"] == "Bundle"

                expected_created_resource_ids = \
                    [created_resource_id for i, created_resource_id in enumerate(created_resource_ids)
                     if i in search.expected_indexes]

                for expected_created_resource_id in expected_created_resource_ids:
                    assert expected_created_resource_id in result_ids
            # else:
            #     assert "entry" in results.keys()
            #     assert isinstance(results["entry"], list)
            #     assert len(results["entry"]) == 0

    except AssertionError:
        cleanup(imms_api, stored_records)
        raise


@pytest.mark.debug
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_search_immunization_accepts_include_and_provides_patient(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """it should require the _include parameter of "Immunization:patient" and return the """

    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    records = [
        {
            "nhs_number": valid_nhs_number1,
            "diseases": [mmr_code],
            "responses": []
        }
    ]
    stored_records = seed_records(imms_api, records)

    try:
        created_resources = [response for resource in stored_records for response in resource["responses"]]
        created_resource_ids = [result["id"] for result in created_resources]

        #response = imms_api.search_immunizations(valid_nhs_number1, "MMR")
        response = imms_api.search_immunizations_full(
            "POST",
            f"patient.identifier={valid_nhs_number_param1}&-immunization.target=MMR&_include=Immunization:patient",
            None)
        #pprint.pprint(response.text)

        assert response.ok
        result = response.json()
        entries = result["entry"]

        entry_ids = [result["resource"]["id"] for result in result["entry"]]
        for created_resource_id in created_resource_ids:
            assert created_resource_id in entry_ids

        patient_entry = next(entry for entry in entries if entry["resource"]["resourceType"] == "Patient")
        assert patient_entry["search"]["mode"] == "include"

        assert patient_entry["resource"]["identifier"][0]["system"] == "https://fhir.nhs.uk/Id/nhs-number"
        assert patient_entry["resource"]["identifier"][0]["value"] == valid_nhs_number1

        datetime.datetime.strptime(patient_entry["resource"]["birthDate"], "%Y-%m-%d").date()

    except Exception:
        cleanup(imms_api, stored_records)
        raise
