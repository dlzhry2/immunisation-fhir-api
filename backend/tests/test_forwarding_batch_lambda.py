import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock
from forwarding_batch_lambda import forward_lambda_handler, ImmunizationBatchController, create_diagnostics_dictionary
import base64
import json
import os
from models.errors import (
    RecordProcessorError,
    CustomValidationError,
    IdentifierDuplicationError,
    ResourceNotFoundError,
    ResourceFoundError,
    MessageNotSuccessfulError,
)
import base64


class TestForwardLambdaHandler(unittest.TestCase):

    def setUp(self):
        """Setup mock clients and helper functions for testing."""
        self.mock_dynamo_client = Mock()
        self.mock_sqs_client = Mock()
        os.environ["DYNAMODB_TABLE_NAME"] = "mock_table_name"

    def tearDown(self):
        """Clean up environment variables after the test."""
        del os.environ["DYNAMODB_TABLE_NAME"]

    def encode_kinesis_payload(self, row):
        """Encodes a row into a base64 string."""
        row_json = json.dumps(row)
        return base64.b64encode(row_json.encode("utf-8")).decode("utf-8")

    def generate_kinesis_rows(self, file_key, row_data):
        """Generate and encode Kinesis rows dynamically based on provided row_data."""
        return [self.encode_kinesis_payload(self.generate_kinesis_row(file_key, *row)) for row in row_data]

    def generate_kinesis_row(self, file_key, row_id, created_at, local_id, operation_requested, supplier, vaccine_type):
        """Generate a single Kinesis row with required attributes."""
        return {
            "file_key": file_key,
            "row_id": row_id,
            "created_at": created_at,
            "local_id": local_id,
            "operation_requested": operation_requested,
            "supplier": supplier,
            "vax_type": vaccine_type,
        }

    def generate_expected_sqs_row(self, file_key, row_id, operation_requested, imms_id=None, diagnostics=None):
        """
        Generate a single row for the expected SQS output.
        If `diagnostics` is provided, include error details in the output.
        """
        row = {
            "file_key": file_key,
            "row_id": row_id,
            "operation_requested": operation_requested,
        }
        if diagnostics:
            row["diagnostics"] = diagnostics
        else:
            row["imms_id"] = imms_id
        return row

    def assert_sqs_output(self, mock_sqs_client, expected_output):
        """Assert that the SQS output matches expectations."""
        mock_sqs_client.send_message.assert_called_once()
        sent_message = json.loads(mock_sqs_client.send_message.call_args[1]["MessageBody"])
        self.assertEqual(len(sent_message), len(expected_output))
        for i, expected_row in enumerate(expected_output):
            self.assertEqual(sent_message[i], expected_row)

    def assert_dynamo_response(self, dynamo_responses, expected_responses):
        """Assert that the DynamoDB responses match expectations."""
        self.assertEqual(len(dynamo_responses), len(expected_responses))
        for i, expected_response in enumerate(expected_responses):
            if isinstance(expected_response, Exception):
                self.assertIsInstance(dynamo_responses[i], type(expected_response))
                self.assertEqual(str(dynamo_responses[i]), str(expected_response))
            else:
                self.assertEqual(dynamo_responses[i], expected_response)

    # def get_test_cases(self):
    #     """Define test cases with Kinesis input rows and expected outputs."""
    #     return [
    #         {
    #             "description": "Test Case 1: All operations succeed",
    #             "file_key": "COVID19_Vaccinations_v5_YGM41_20240909T13005902.csv",
    #             "kinesis_rows": self.generate_kinesis_rows(
    #                 "file1",
    #                 [
    #                     ("321", "2025-01-01T12:00:00Z", "local321", "CREATE", "supplier1", "type1"),
    #                 ],
    #             ),
    #             "expected_dynamo_responses": ["imms_id_321", "imms_id_654", "imms_id_987"],
    #             "expected_sqs_output": [
    #                 self.generate_expected_sqs_row("file1", "321", "CREATE", imms_id="imms_id_321")
    #             ],
    #         },
    #     ]

    # def test_forward_lambda_handler(self):
    #     """Test the forward_lambda_handler with multiple test cases."""
    #     for test_case in self.get_test_cases():
    #         with self.subTest(msg=test_case["description"]):

    #             kinesis_event = {
    #                 "Records": [{"kinesis": {"data": json.dumps(row)}} for row in test_case["kinesis_rows"]]
    #             }
    #             print(f"KINESIS EVENT: {kinesis_event}")
    #             self.mock_dynamo_client.query.side_effect = test_case["expected_dynamo_responses"]

    #             forward_lambda_handler(kinesis_event, "_")

    #             # Assert SQS output
    #             self.assert_sqs_output(self.mock_sqs_client, test_case["expected_sqs_output"])

    #             # Assert DynamoDB responses
    #             dynamo_responses = [call[1]["Response"] for call in self.mock_dynamo_client.method_calls]
    #             self.assert_dynamo_response(dynamo_responses, test_case["expected_dynamo_responses"])

    def test_create_diagnostics_dictionary(self):

        test_cases = [
            {
                "error": RecordProcessorError("Diagnostics from recordprocessor"),
                "expected_output": "Diagnostics from recordprocessor",
            },
            {
                "error": CustomValidationError("Validation failed"),
                "expected_output": {
                    "error_type": "CustomValidationError",
                    "statusCode": 400,
                    "error_message": "Validation failed",
                },
            },
            {
                "error": IdentifierDuplicationError("Duplicate identifier"),
                "expected_output": {
                    "error_type": "IdentifierDuplicationError",
                    "statusCode": 422,
                    "error_message": "The provided identifier: Duplicate identifier is duplicated",
                },
            },
            {
                "error": ResourceNotFoundError(resource_type="Immunization", resource_id=None),
                "expected_output": {
                    "error_type": "ResourceNotFoundError",
                    "statusCode": 404,
                    "error_message": "Immunization resource does not exist. ID: None",
                },
            },
            {
                "error": ResourceFoundError(resource_type="Immunization", resource_id="A-primary-key"),
                "expected_output": {
                    "error_type": "ResourceFoundError",
                    "statusCode": 409,
                    "error_message": "Immunization resource does exist. ID: A-primary-key",
                },
            },
            {
                "error": MessageNotSuccessfulError("Message processing failed"),
                "expected_output": {
                    "error_type": "MessageNotSuccessfulError",
                    "statusCode": 500,
                    "error_message": "Message processing failed",
                },
            },
            {
                "error": Exception("General exception"),
                "expected_output": {
                    "error_type": "Exception",
                    "statusCode": 500,
                    "error_message": "General exception",
                },
            },
        ]

        for case in test_cases:
            with self.subTest(error=case["error"]):
                result = create_diagnostics_dictionary(case["error"])
                self.assertEqual(result, case["expected_output"])


if __name__ == "__main__":
    unittest.main()
