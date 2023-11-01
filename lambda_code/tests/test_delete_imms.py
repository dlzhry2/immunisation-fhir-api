from unittest.mock import MagicMock
import unittest
import json
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from delete_imms_handler import delete_imms_handler


class TestDeleteImms(unittest.TestCase):
    def setUp(self):
        self.dynamodb_service = EventTable()

    def test_delete_imms_happy_path(self):
        #Arrange
        self.dynamodb_service.delete_event = MagicMock(return_value={"statusCode": 200, "body": "Item deleted"})
        formatted_event = { "pathParameters" : {"id": "sampleid"} }

        #Act
        result = delete_imms_handler(formatted_event, self.dynamodb_service)

        #Assert
        self.dynamodb_service.delete_event.assert_called_once_with(formatted_event["pathParameters"]["id"])
        assert result['statusCode'] == 200
        assert json.loads(result['body']) == {"statusCode": 200, "body": "Item deleted"}