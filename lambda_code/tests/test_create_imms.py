import json
import os
import sys
import unittest
import uuid
from unittest.mock import create_autospec

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from create_imms_handler import create_immunization
from fhir_controller import FhirController
from models.errors import Severity, Code, create_operation_outcome


class TestDeleteImmunizationById(unittest.TestCase):
    def setUp(self):
        self.controller = create_autospec(FhirController)

    def test_create_immunization(self):
        """it should create Immunization"""
        lambda_event = {"pathParameters": {"id": "an-id"}}
        exp_res = {"a-key": "a-value"}

        self.controller.create_immunization.return_value = exp_res

        # When
        act_res = create_immunization(lambda_event, self.controller)

        # Then
        self.controller.create_immunization.assert_called_once_with(lambda_event)
        self.assertDictEqual(exp_res, act_res)

    def test_handle_exception(self):
        """unhandled exceptions should result in 500"""
        lambda_event = {"pathParameters": {"id": "an-id"}}
        error_msg = "an unhandled error"
        self.controller.create_immunization.side_effect = Exception(error_msg)

        exp_error = create_operation_outcome(resource_id=str(uuid.uuid4()), severity=Severity.error,
                                             code=Code.server_error,
                                             diagnostics=error_msg)

        # When
        act_res = create_immunization(lambda_event, self.controller)

        # Then
        act_body = json.loads(act_res["body"])
        act_body["id"] = None
        exp_body = json.loads(exp_error.json())  # to and from json so, we get from OrderedDict to Dict
        exp_body["id"] = None

        self.assertDictEqual(act_body, exp_body)
        self.assertEqual(act_res["statusCode"], 500)
