from unittest.mock import MagicMock
import unittest
import json
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from get_imms_handler import get_imms


def test_get_imms_handler_sad_path():
    # Arrange
    unformatted_event = {"id": "unexpected_id"}

    # Act
    result = get_imms(unformatted_event, None)

    # Assert
    assert result['statusCode'] == 400
    assert result['body'] == 'ID is not formatted correctly or is missing'
    
# Build 404 test


class TestGetImms(unittest.TestCase):
    def setUp(self):
        self.dynamodb_service = EventTable()

    def test_get_imms_happy_path(self):
        #Arrange
        self.dynamodb_service.get_event_by_id = MagicMock(return_value="Mocked event data")
        formatted_event = { "id": "sampleid" }
        
        #Act
        result = get_imms(formatted_event, self.dynamodb_service)
        
        #Assert
        self.dynamodb_service.get_event_by_id.assert_called_once_with(formatted_event["id"])
        assert result['statusCode'] == 200
        assert json.loads(result['body']) == {"message": "Mocked event data"}

    def test_get_imms_handler_sad_path(self):
        unformatted_event = {"id": "unexpected_id"}

        # Act
        result = get_imms(unformatted_event, None)

        # Assert
        assert result['statusCode'] == 400
        assert result['body'] == 'ID is not formatted correctly or is missing'