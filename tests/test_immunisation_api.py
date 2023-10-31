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
    #Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    #Act
    result = imms_api.get_event_by_id("some-id-that-does-not-exist")

    #Assert
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
    #Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    #Act
    result = imms_api.get_event_by_id("some_id_that_is_malformed")

    #Assert
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


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_event_by_id_happy_path_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    #Arrange
    token = nhsd_apim_auth_headers["Authorization"]
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)

    #Act
    result = imms_api.get_event_by_id("e045626e-4dc5-4df3-bc35-da25263f901e")

    #Assert
    assert result.status_code == 200
    assert result.json() == {'resourceType': 'Immunization', 'contained': [{'resourceType': 'QuestionnaireResponse', 'questionnaire': 'Questionnaire/1', 'status': 'completed', 'item': [{'linkId': 'SiteCode', 'answer': [{'valueCoding': {'system': 'snomed', 'code': 'M242ND'}}]}, {'linkId': 'SiteName', 'answer': [{'valueCoding': {'code': 'dummy'}}]}, {'linkId': 'NhsNumberStatus', 'answer': [{'valueCoding': {'code': 'snomed', 'display': 'test description'}}]}, {'linkId': 'LocalPatient', 'answer': [{'valueCoding': {'system': 'https://supplierABC/identifiers/patient', 'code': 'ACME-patient123456'}}]}, {'linkId': 'Consent', 'answer': [{'valueCoding': {'code': 'snomed', 'display': 'free text'}}]}, {'linkId': 'CareSetting', 'answer': [{'valueCoding': {'code': '1127531000000102', 'display': 'SNOMED-CT Term description Community health services (qualifier value)'}}]}, {'linkId': 'IpAddress', 'answer': [{'valueCoding': {'code': '1.0.0.0'}}]}, {'linkId': 'UserId', 'answer': [{'valueCoding': {'code': 'test123'}}]}, {'linkId': 'UserName', 'answer': [{'valueCoding': {'code': 'test'}}]}, {'linkId': 'UserEmail', 'answer': [{'valueCoding': {'code': 'test@gmail.com'}}]}, {'linkId': 'SubmittedTimeStamp', 'answer': [{'valueCoding': {'code': '2020-12-14T10:08:15'}}]}, {'linkId': 'ReduceValidation', 'answer': [{'valueCoding': {'code': 'TRUE', 'display': 'test'}}]}]}], 'extension': [{'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure', 'valueCodeableConcept': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'snomed', 'display': 'snomed'}]}}, {'url': 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation', 'valueCodeableConcept': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'snomed', 'display': 'snomed'}]}}], 'identifier': [{'system': 'https://supplierABC/ODSCode', 'value': 'e045626e-4dc5-4df3-bc35-da25263f901e'}], 'status': 'completed', 'statusReason': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'snomed', 'display': 'snomed'}]}, 'vaccineCode': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'snomed', 'display': 'snomed'}]}, 'lotNumber': 'AAJN11K', 'expirationDate': '2020-05-06', 'patient': {'resourceType': 'Patient', 'identifier': [{'system': 'https//fhir.nhs.uk/Id/nhs-number', 'value': '1234567891'}], 'name': [{'family': 'test', 'given': ['test']}], 'gender': '1', 'birthDate': '1999-10-03', 'address': [{'postalCode': 'LS1 5HT'}]}, 'occurrenceDateTime': '2020-12-14T10:08:15+00:00', 'primarySource': True, 'location': {'identifier': {'system': 'https://fhir.nhs.uk/Id/ods-organization-code', 'value': 'B0C4P'}, 'resourceType': 'Location'}, 'site': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'LA', 'display': 'left arm'}]}, 'route': {'coding': [{'system': 'http://snomed.info/sct', 'code': 'IM', 'display': 'injection, intramuscular'}]}, 'doseQuantity': {'value': 5, 'unit': 'mg', 'system': 'http://unitsofmeasure.org', 'code': 'snomed'}, 'protocolApplied': [{'targetDisease': [{'coding': [{'code': '40468003'}]}], 'doseNumber': '5'}], 'reportOrigin': {'text': 'sample'}, 'reasonCode': [{'coding': [{'code': 'snomed', 'display': 'test'}]}], 'recorded': '2010-05-06', 'manufacturer': {'resourceType': 'Organization', 'name': 'org'}, 'performer': {'actor': {'resourceType': 'Practitioner', 'identifier': [{'type': {'coding': [{'display': 'GP'}]}, 'system': 'https://fhir.hl7.org.uk/Id/gmc-number', 'value': 'OP'}], 'name': [{'family': 'test', 'given': ['test']}]}}}


@pytest.mark.smoketest
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "application",
        "level": "level3"
    })
def test_get_event_by_id_not_found_app_restricted(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # TODO same here but with app restricted, probably refactor both into a function instead of copy paste
    # token = nhsd_apim_auth_headers["access_token"]  # <- not tested
    token = "token"
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    res = imms_api.get_event_by_id("some-id-that-does-not-exist")
    # Make assertions
