import json
import unittest
from unittest.mock import patch
import uuid

from fhir_controller import FhirController
from models.errors import Severity, Code, create_operation_outcome
from update_imms_handler import update_imms
from constants import GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE


class TestUpdateImmunizations(unittest.TestCase):
    MOCK_RESOURCE_UUID = "6627941a-9c5a-4d0f-adce-dfe29dd38413"

    def setUp(self):
        self.mock_controller = patch("update_imms_handler.controller", autospec=FhirController).start()
        self.logger_exception_patcher = patch("logging.Logger.exception")
        self.mock_logger_exception = self.logger_exception_patcher.start()

    def tearDown(self):
        patch.stopall()

    def test_update_immunization(self):
        """it should call service update method"""
        lambda_event = {"pathParameters": {"id": "an-id"}}
        exp_res = {"a-key": "a-value"}

        self.mock_controller.update_immunization.return_value = exp_res

        # When
        act_res = update_imms(lambda_event)

        # Then
        self.mock_controller.update_immunization.assert_called_once_with(lambda_event)
        self.assertDictEqual(exp_res, act_res)

    @patch("update_imms_handler.uuid", autospec=uuid)
    def test_update_imms_exception(self, mock_uuid):
        """unhandled exceptions should result in 500"""
        lambda_event = {"pathParameters": {"id": "an-id"}}
        error_msg = "an unhandled error"
        mock_uuid.uuid4.return_value = self.MOCK_RESOURCE_UUID
        self.mock_controller.update_immunization.side_effect = Exception(error_msg)

        exp_error = create_operation_outcome(
            resource_id=self.MOCK_RESOURCE_UUID,
            severity=Severity.error,
            code=Code.server_error,
            diagnostics=GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE,
        )

        # When
        act_res = update_imms(lambda_event)

        # Then
        self.mock_controller.update_immunization.assert_called_once_with(lambda_event)
        self.mock_logger_exception.assert_called_once_with("Unhandled exception")
        act_body = json.loads(act_res["body"])

        self.assertDictEqual(act_body, exp_error)
        self.assertEqual(act_res["statusCode"], 500)

    def test_update_imms_with_duplicated_identifier_returns_error(self):
        """Should return an IdentifierDuplication error"""
        lambda_event = {"pathParameters": {"id": "an-id"}}
        error_msg = {
            "statusCode": 422,
            "headers": {"Content-Type": "application/fhir+json"},
            "body": '{"resourceType": "OperationOutcome", "id": "5c132d8a-a928-4e0e-8792-0c6456e625c2", "meta": {"profile": ["https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"]}, "issue": [{"severity": "error", "code": "exception", "details": {"coding": [{"system": "https://fhir.nhs.uk/Codesystem/http-error-codes","code": "DUPLICATE"}]}, "diagnostics": "The provided identifier: id-id is duplicated"}]}',
        }
        self.mock_controller.update_immunization.return_value = error_msg

        act_res = update_imms(lambda_event)

        # Then
        self.mock_controller.update_immunization.assert_called_once_with(lambda_event)
        self.assertEqual(act_res["statusCode"], 422)
        self.assertDictEqual(act_res, error_msg)
