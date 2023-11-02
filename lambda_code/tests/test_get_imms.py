import uuid
from unittest.mock import MagicMock
import unittest
import json
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from get_imms_handler import get_imms, create_response


class TestGetImms(unittest.TestCase):
    def setUp(self):
        self.dynamodb_service = EventTable()

    def test_get_imms_happy_path(self):
        # Arrange
        self.dynamodb_service.get_event_by_id = MagicMock(return_value={"message": "Mocked event data"})
        formatted_event = {"pathParameters": {"id": "sampleid"}}

        # Act
        result = get_imms(formatted_event, self.dynamodb_service)

        # Assert
        self.dynamodb_service.get_event_by_id.assert_called_once_with(formatted_event["pathParameters"]["id"])
        assert result['statusCode'] == 200
        self.assertEqual(result['headers']['Content-Type'], "application/fhir+json")
        assert json.loads(result['body']) == {"message": "Mocked event data"}

    def test_get_imms_handler_sad_path_400(self):
        unformatted_event = {"pathParameters": {"id": "unexpected_id"}}

        # Act
        result = get_imms(unformatted_event, None)

        # Assert
        assert result['statusCode'] == 400
        self.assertEqual(result['headers']['Content-Type'], "application/fhir+json")
        act_body = json.loads(result['body'])
        exp_body = create_response("The provided event ID is either missing or not in the expected format.", "invalid")
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
        exp_body = create_response("The requested resource was not found.", "not-found")
        act_body["id"] = None
        exp_body["id"] = None
        self.assertDictEqual(act_body, exp_body)
