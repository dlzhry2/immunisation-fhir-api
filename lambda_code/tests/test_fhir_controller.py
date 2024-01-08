import json
import os
import sys
import unittest
from unittest.mock import create_autospec

from fhir.resources.immunization import Immunization
from fhir.resources.list import List

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_controller import FhirController
from fhir_service import FhirService
from models.errors import ResourceNotFoundError, UnhandledResponseError, InvalidPatientId


def _create_a_post_event(body: str) -> dict:
    return {"version": "2.0", "routeKey": "POST /event", "rawPath": "/jaho3/event", "rawQueryString": "",
            "headers": {"accept-encoding": "br,deflate,gzip,x-gzip", "content-length": "688",
                        "content-type": "application/fhir+json", "host": "jaho3.imms.dev.api.platform.nhs.uk",
                        "user-agent": "Apache-HttpClient/4.5.14 (Java/17.0.8.1)",
                        "x-amzn-trace-id": "Root=1-6556ab07-72760aca0fdf068e5997f65a",
                        "x-forwarded-for": "81.110.196.79", "x-forwarded-port": "443", "x-forwarded-proto": "https"},
            "requestContext": {"accountId": "790083933819", "apiId": "bgllbuiz2i",
                               "domainName": "jaho3.imms.dev.api.platform.nhs.uk", "domainPrefix": "jaho3",
                               "http": {"method": "POST", "path": "/jaho3/event", "protocol": "HTTP/1.1",
                                        "sourceIp": "81.110.196.79",
                                        "userAgent": "Apache-HttpClient/4.5.14 (Java/17.0.8.1)"},
                               "requestId": "Og-pShuvLPEEM1Q=", "routeKey": "POST /event", "stage": "jaho3",
                               "time": "16/Nov/2023:23:51:35 +0000", "timeEpoch": 1700178695954},
            "body": "{\n  \"resourceType\": \"Immunization\",\n  \"id\": \"e045626e-4dc5-4df3-bc35-da25263f901e\",\n  \"identifier\": [\n    {\n      \"system\": \"https://supplierABC/ODSCode\",\n      \"value\": \"e045626e-4dc5-4df3-bc35-da25263f901e\"\n    }\n  ],\n  \"status\": \"completed\",\n  \"vaccineCode\": {\n    \"coding\": [\n      {\n        \"system\": \"http://snomed.info/sct\",\n        \"code\": \"39114911000001105\",\n        \"display\": \"some text\"\n      }\n    ]\n  },\n  \"patient\": {\n    \"reference\": \"urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec\",\n    \"type\": \"Patient\",\n    \"identifier\": {\n      \"system\": \"https://fhir.nhs.uk/Id/nhs-number\",\n      \"value\": \"9000000009\"\n    }\n  },\n  \"occurrenceDateTime\": \"2020-12-14T10:08:15+00:00\"\n}",
            "isBase64Encoded": False}


class TestFhirController(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_create_response(self):
        """it should return application/fhir+json with correct status code"""
        res = self.controller.create_response(42, "a body")
        headers = res["headers"]

        self.assertEqual(res["statusCode"], 42)
        self.assertDictEqual(headers, {
            "Content-Type": "application/fhir+json",
        })
        self.assertEqual(res["body"], "a body")


class TestFhirControllerGetImmunizationById(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_get_imms_by_id(self):
        """it should return Immunization resource if it exists"""
        # Given
        imms_id = "a-id"
        self.service.get_immunization_by_id.return_value = Immunization.construct()
        lambda_event = {"pathParameters": {"id": imms_id}}

        # When
        response = self.controller.get_immunization_by_id(lambda_event)

        # Then
        self.service.get_immunization_by_id.assert_called_once_with(imms_id)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "Immunization")

    def test_not_found(self):
        """it should return not-found OperationOutcome if it doesn't exist"""
        # Given
        imms_id = "a-non-existing-id"
        self.service.get_immunization_by_id.return_value = None
        lambda_event = {"pathParameters": {"id": imms_id}}

        # When
        response = self.controller.get_immunization_by_id(lambda_event)

        # Then
        self.service.get_immunization_by_id.assert_called_once_with(imms_id)

        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertEqual(body["issue"][0]["code"], "not-found")

    def test_validate_imms_id(self):
        """it should validate lambda's Immunization id"""
        invalid_id = {"pathParameters": {"id": "invalid %$ id"}}

        response = self.controller.get_immunization_by_id(invalid_id)

        self.assertEqual(self.service.get_immunization_by_id.call_count, 0)
        self.assertEqual(response["statusCode"], 400)
        outcome = json.loads(response["body"])
        self.assertEqual(outcome["resourceType"], "OperationOutcome")


class TestCreateImmunization(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_create_immunization(self):
        """it should create Immunization"""
        imms = Immunization.construct()
        aws_event = {"body": imms.json()}
        self.service.create_immunization.return_value = imms

        response = self.controller.create_immunization(aws_event)

        self.service.create_immunization.assert_called_once_with(imms)
        self.assertEqual(response["statusCode"], 201)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "Immunization")

    def test_malformed_resource(self):
        """it should return 400 if json is malformed"""
        bad_json = "{foo: \"bar\"}"
        aws_event = {"body": bad_json}

        response = self.controller.create_immunization(aws_event)

        self.assertEqual(self.service.get_immunization_by_id.call_count, 0)
        self.assertEqual(response["statusCode"], 400)
        outcome = json.loads(response["body"])
        self.assertEqual(outcome["resourceType"], "OperationOutcome")

    def test_invalid_nhs_number(self):
        """it should handle ValidationError when patient doesn't exist"""
        imms = Immunization.construct()
        aws_event = {"body": imms.json()}
        invalid_nhs_num = "a-bad-id"
        self.service.create_immunization.side_effect = InvalidPatientId(nhs_number=invalid_nhs_num)

        response = self.controller.create_immunization(aws_event)

        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertTrue(invalid_nhs_num in body["issue"][0]["diagnostics"])

    def test_pds_unhandled_error(self):
        """it should respond with 500 if PDS returns error"""
        imms = Immunization.construct()
        aws_event = {"body": imms.json()}
        self.service.create_immunization.side_effect = UnhandledResponseError(response={}, message="a message")

        response = self.controller.create_immunization(aws_event)

        self.assertEqual(500, response["statusCode"])
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")


class TestDeleteImmunization(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_validate_imms_id(self):
        """it should validate lambda's Immunization id"""
        invalid_id = {"pathParameters": {"id": "invalid %$ id"}}

        response = self.controller.delete_immunization(invalid_id)

        self.assertEqual(self.service.get_immunization_by_id.call_count, 0)
        self.assertEqual(response["statusCode"], 400)
        outcome = json.loads(response["body"])
        self.assertEqual(outcome["resourceType"], "OperationOutcome")

    def test_delete_immunization(self):
        # Given
        imms_id = "an-id"
        self.service.delete_immunization.return_value = Immunization.construct()
        lambda_event = {"pathParameters": {"id": imms_id}}

        # When
        response = self.controller.delete_immunization(lambda_event)

        # Then
        self.service.delete_immunization.assert_called_once_with(imms_id)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "Immunization")

    def test_immunization_exception_not_found(self):
        """it should return not-found OperationOutcome if service throws ResourceNotFoundError"""
        # Given
        error = ResourceNotFoundError(resource_type="Immunization", resource_id="an-error-id")
        self.service.delete_immunization.side_effect = error
        lambda_event = {"pathParameters": {"id": "a-non-existing-id"}}

        # When
        response = self.controller.delete_immunization(lambda_event)

        # Then
        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertEqual(body["issue"][0]["code"], "not-found")

    def test_immunization_unhandled_error(self):
        """it should return server-error OperationOutcome if service throws UnhandledResponseError"""
        # Given
        error = UnhandledResponseError(message="a message", response={})
        self.service.delete_immunization.side_effect = error
        lambda_event = {"pathParameters": {"id": "a-non-existing-id"}}

        # When
        response = self.controller.delete_immunization(lambda_event)

        # Then
        self.assertEqual(response["statusCode"], 500)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertEqual(body["issue"][0]["code"], "internal-server-error")


class TestSearchImmunizations(unittest.TestCase):
    def setUp(self):
        self.service = create_autospec(FhirService)
        self.controller = FhirController(self.service)

    def test_search_immunizations(self):
        """it should search based on nhsNumber and diseaseType"""
        search_result = List.construct()
        self.service.search_immunizations.return_value = search_result

        nhs_number = "an-patient-id"
        disease_type = "a-disease-type"
        lambda_event = {"queryStringParameters": {
            "diseaseType": disease_type,
            "nhsNumber": nhs_number
        }}

        # When
        response = self.controller.search_immunizations(lambda_event)

        # Then
        self.service.search_immunizations.assert_called_once_with(nhs_number, disease_type)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "List")

    def test_nhs_number_is_mandatory(self):
        """nhsNumber is a mandatory query param"""
        lambda_event = {"queryStringParameters": {
            "diseaseType": "a-disease-type",
        }}

        response = self.controller.search_immunizations(lambda_event)

        self.assertEqual(self.service.search_immunizations.call_count, 0)
        self.assertEqual(response["statusCode"], 400)
        outcome = json.loads(response["body"])
        self.assertEqual(outcome["resourceType"], "OperationOutcome")

    def test_diseaseType_is_mandatory(self):
        """diseaseType is a mandatory query param"""
        lambda_event = {"queryStringParameters": {
            "nhsNumber": "an-id",
        }}

        response = self.controller.search_immunizations(lambda_event)

        self.assertEqual(self.service.search_immunizations.call_count, 0)
        self.assertEqual(response["statusCode"], 400)
        outcome = json.loads(response["body"])
        self.assertEqual(outcome["resourceType"], "OperationOutcome")
