import json
import os
import sys
import unittest
from unittest.mock import create_autospec

from fhir.resources.immunization import Immunization

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_controller import FhirController
from fhir_service import FhirService


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


class TestFhirControllerGetImmunisationById(unittest.TestCase):
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

    def test_not_found(self):
        """it should return not-found OperationOutcome if it doesn't exist"""
        # Given
        imms_id = "a-non-existing-id"
        self.service.delete_immunization.return_value = None
        lambda_event = {"pathParameters": {"id": imms_id}}

        # When
        response = self.controller.delete_immunization(lambda_event)

        # Then
        self.service.delete_immunization.assert_called_once_with(imms_id)

        self.assertEqual(response["statusCode"], 404)
        body = json.loads(response["body"])
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertEqual(body["issue"][0]["code"], "not-found")
