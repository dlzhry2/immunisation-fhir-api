import pytest
import requests


class ImmunisationApi:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_event_by_id(self, event_id):
        headers = {
            "Authorization": self.token
        }
        response = requests.get(f"{self.url}/event/{event_id}", headers=headers)
        return response


# TODO: send a GET /event/{id} request
# This should give you 404 not found, since there is no event yet (we don't have POST)
# Test happy test manually. In both scenarios make sure lambda is getting executed
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
    result = imms_api.get_event_by_id("some-id-that-does-not-exist")

    # Assert
    assert result.status_code == 404
    assert result.json() == {
            "resourceType": "OperationOutcome",
            "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
            "meta": {
                "profile": [
                    "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "error",
                    "code": "not-found",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                "code": "NOT_FOUND"
                            }
                        ]
                    },
                    "diagnostics": "The requested resource was not found."
                }
            ]
        }


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
    result = imms_api.get_event_by_id("some_id_that_is_malformed")

    # Assert
    assert result.status_code == 400
    assert result.json() == {
            "resourceType": "OperationOutcome",
            "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
            "meta": {
                "profile": [
                    "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
                ]
            },
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
                                "code": "INVALID"
                            }
                        ]
                    },
                    "diagnostics": "The provided event ID is either missing or not in the expected format."
                }
            ]
        }


@pytest.mark.debug
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_event_by_id_happy_path_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    # Act
    id = "e045626e-4dc5-4df3-bc35-da25263f901e"
    result = imms_api.get_event_by_id(id)
    json_result = result.json()

    # Assert
    assert result.status_code == 200
    assert json_result["identifier"][0]["value"] == id


# @pytest.mark.smoketest
# @pytest.mark.nhsd_apim_authorization(
#    {
#        "access": "application",
#        "level": "level3"
#    })
# def test_get_event_by_id_not_found_app_restricted(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # TODO same here but with app restricted, probably refactor both into a function instead of copy paste
    # token = nhsd_apim_auth_headers["access_token"]  # <- not tested
    # token = "token"
    # imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    # res = imms_api.get_event_by_id("some-id-that-does-not-exist")
    # Make assertions
