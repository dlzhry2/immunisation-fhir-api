import json
import unittest
from unittest.mock import patch
import uuid

from fhir_controller import FhirController
from get_imms_handler import get_immunization_by_id
from models.errors import Severity, Code, create_operation_outcome
from constants import GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE



class TestGetImmunisationById(unittest.TestCase):
    MOCK_RESOURCE_UUID = "6627941a-9c5a-4d0f-adce-dfe29dd38413"

    def setUp(self):
        self.logger_exception_patcher = patch("logging.Logger.exception")
        self.mock_logger_exception = self.logger_exception_patcher.start()

    def tearDown(self):
        patch.stopall()

    @patch("get_imms_handler.controller", autospec=FhirController)
    def test_get_immunization_by_id(self, mock_controller):
        """it should get the given Immunization by id"""
        lambda_event = {"headers": {"id": "an-id"}, "pathParameters": {"id": "an-id"}}
        exp_res = {"a-key": "a-value"}

        mock_controller.get_immunization_by_id.return_value = exp_res

        # When
        act_res = get_immunization_by_id(lambda_event)

        # Then
        mock_controller.get_immunization_by_id.assert_called_once_with(lambda_event)
        self.assertDictEqual(exp_res, act_res)

    @patch("get_imms_handler.uuid", autospec=uuid)
    @patch("get_imms_handler.controller", autospec=FhirController)
    def test_handle_exception(self, mock_controller, mock_uuid):
        """unhandled exceptions should result in 500"""
        lambda_event = {"headers": {"id": "an-id"}, "pathParameters": {"id": "an-id"}}
        error_msg = "an unhandled error"
        mock_uuid.uuid4.return_value = self.MOCK_RESOURCE_UUID
        mock_controller.get_immunization_by_id.side_effect = Exception(error_msg)

        exp_error = create_operation_outcome(
            resource_id=self.MOCK_RESOURCE_UUID,
            severity=Severity.error,
            code=Code.server_error,
            diagnostics=GENERIC_SERVER_ERROR_DIAGNOSTICS_MESSAGE,
        )

        # When
        act_res = get_immunization_by_id(lambda_event,)

        # Then
        mock_controller.get_immunization_by_id.assert_called_once_with(lambda_event)
        self.mock_logger_exception.assert_called_once_with("Unhandled exception")
        act_body = json.loads(act_res["body"])

        self.assertDictEqual(act_body, exp_error)
        self.assertEqual(act_res["statusCode"], 500)
