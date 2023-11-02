import json
import os
import sys
import unittest
import uuid
from unittest.mock import MagicMock, create_autospec

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from get_imms_handler import get_imms, create_operation_outcome


class TestGetImmunisationById(unittest.TestCase):
    def setUp(self):
        self.dynamodb_service = create_autospec(EventTable)

    def test_get_imms_happy_path(self):
        # Arrange
        self.dynamodb_service.get_event_by_id = MagicMock(return_value={"message": "Mocked event data"})
        lambda_event = {"pathParameters": {"id": "sample-id"}}

        # Act
        result = get_imms(lambda_event, self.dynamodb_service)

        # Assert
        self.dynamodb_service.get_event_by_id.assert_called_once_with(lambda_event["pathParameters"]["id"])
        self.assertEqual(result['statusCode'], 200)
        self.assertDictEqual(json.loads(result['body']), {"message": "Mocked event data"})

    def test_get_imms_handler_sad_path_400(self):
        unformatted_event = {"pathParameters": {"id": "unexpected_id"}}

        # Act
        result = get_imms(unformatted_event, None)

        # Assert
        assert result['statusCode'] == 400
        act_body = json.loads(result['body'])
        exp_body = create_operation_outcome(str(uuid.uuid4()),
                                            "he provided event ID is either missing or not in the expected format.",
                                            "invalid")
        act_body["id"] = None
        exp_body["id"] = None
        self.assertDictEqual(act_body, exp_body)

    def test_get_imms_handler_sad_path_404(self):
        # Arrange
        self.dynamodb_service.get_event_by_id = MagicMock(return_value=None)
        incorrect_event = {"pathParameters": {"id": "incorrectid"}}

        # Act
        result = get_imms(incorrect_event, self.dynamodb_service)

        # Assert
        assert result['statusCode'] == 404
        self.assertEqual(result['headers']['Content-Type'], "application/fhir+json")
        act_body = json.loads(result['body'])
        exp_body = create_operation_outcome(str(uuid.uuid4()), "The requested resource was not found.", "not-found")
        act_body["id"] = None
        exp_body["id"] = None
        self.assertDictEqual(act_body, exp_body)
