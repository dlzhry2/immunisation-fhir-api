from unittest.mock import MagicMock
import unittest
import sys
import os

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from dynamodb import EventTable
from delete_imms_handler import delete_imms


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
        self.dynamodb_service.delete_event.assert_called_once_with(formatted_event["pathParameters"]["id"])
        assert result['statusCode'] == 200
        assert result['body'] == "Item deleted"
        
    # def test_delete_imms_handler_sad_path_400(self):
    #     unformatted_event = { "pathParameters" : {"id": "unformatted_id"} }

    #     # Act
    #     result = delete_imms(unformatted_event, None)
    #     print(result['body'], "<<<<<<<<<< RESULT")
        
    #     # Assert
    #     assert result['statusCode'] == 400
    #     assert result['body'] == {
    #         "resourceType": "OperationOutcome",
    #         "id": "a5abca2a-4eda-41da-b2cc-95d48c6b791d",
    #         "meta": {
    #             "profile": [
    #                 "https://simplifier.net/guide/UKCoreDevelopment2/ProfileUKCore-OperationOutcome"
    #             ]
    #         },
    #         "issue": [
    #             {
    #                 "severity": "error",
    #                 "code": "invalid",
    #                 "details": {
    #                     "coding": [
    #                         {
    #                             "system": "https://fhir.nhs.uk/Codesystem/http-error-codes",
    #                             "code": "INVALID"
    #                         }
    #                     ]
    #                 },
    #                 "diagnostics": "The provided event ID is either missing or not in the expected format."
    #             }
    #         ]
    #     }