from unittest.mock import MagicMock
import unittest
import sys
import os
import json

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from delete_imms_handler import delete_imms, create_response


class TestDeleteImms(unittest.TestCase):
    def setUp(self):
        self.dynamodb_service = EventTable()

    def test_delete_imms_happy_path(self):
        #Arrange
        self.dynamodb_service.delete_event = MagicMock(return_value="Item deleted")
        formatted_event = { "pathParameters" : {"id": "sampleid"} }

        #Act
        result = delete_imms(formatted_event, self.dynamodb_service)

        #Assert
        # self.assertEqual(result['headers']['Content-Type'], "application/fhir+json")
        self.dynamodb_service.delete_event.assert_called_once_with(formatted_event["pathParameters"]["id"])
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['body'], "Item deleted")
        
    def test_delete_imms_handler_sad_path_400(self):
        unformatted_event = { "pathParameters" : {"id": "unformatted_id"} }

        # Act
        result = delete_imms(unformatted_event, None)
        
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
        self.dynamodb_service.delete_event = MagicMock(return_value=None)
        incorrect_event = {"pathParameters": {"id": "incorrectid"}}

        # Act
        result = delete_imms(incorrect_event, self.dynamodb_service)

        # Assert
        assert result['statusCode'] == 404
        self.assertEqual(result['headers']['Content-Type'], "application/fhir+json")
        act_body = json.loads(result['body'])
        exp_body = create_response("The requested resource was not found.", "not-found")
        act_body["id"] = None
        exp_body["id"] = None
        self.assertDictEqual(act_body, exp_body)
        