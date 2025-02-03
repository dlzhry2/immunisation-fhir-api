"""Tests for the ack processor lambda handler."""

import unittest
import os
import json
from unittest.mock import patch
from io import StringIO
from boto3 import client as boto3_client
from moto import mock_s3, mock_firehose

from tests.utils_for_ack_backend_tests.values_for_ack_backend_tests import ValidValues, DiagnosticsDictionaries
from tests.utils_for_ack_backend_tests.mock_environment_variables import MOCK_ENVIRONMENT_DICT, BucketNames, REGION_NAME
from tests.utils_for_ack_backend_tests.generic_setup_and_teardown_for_ack_backend import GenericSetUp, GenericTearDown
from tests.utils_for_ack_backend_tests.utils_for_ack_backend_tests import (
    MOCK_MESSAGE_DETAILS,
    generate_expected_ack_content,
    setup_existing_ack_file,
    obtain_current_ack_file_content,
)

with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from ack_processor import lambda_handler

s3_client = boto3_client("s3", region_name=REGION_NAME)
firehose_client = boto3_client("firehose", region_name=REGION_NAME)


@patch.dict(os.environ, MOCK_ENVIRONMENT_DICT)
@mock_s3
@mock_firehose
class TestAckProcessor(unittest.TestCase):
    """Tests for the ack processor lambda handler."""

    def setUp(self) -> None:
        GenericSetUp(s3_client, firehose_client)

        # MOCK SOURCE FILE WITH 100 ROWS TO SIMULATE THE SCENARIO WHERE THE ACK FILE IS NO FULL.
        # TODO: Test all other scenarios.
        mock_source_file_with_100_rows = StringIO("\n".join(f"Row {i}" for i in range(1, 101)))
        s3_client.put_object(
            Bucket=BucketNames.SOURCE,
            Key=f"processing/{MOCK_MESSAGE_DETAILS.file_key}",
            Body=mock_source_file_with_100_rows.getvalue(),
        )

    def tearDown(self) -> None:
        GenericTearDown(s3_client, firehose_client)

    @staticmethod
    def generate_event(test_messages: list[dict]) -> dict:
        """
        Returns an event where each message in the incoming message body list is based on a standard mock message,
        updated with the details from the corresponsing message in the given test_messages list.
        """
        incoming_message_body = [{**MOCK_MESSAGE_DETAILS.message, **message} for message in test_messages]
        return {"Records": [{"body": json.dumps(incoming_message_body)}]}

    def validate_ack_file_content(
        self, incoming_messages: list[dict], existing_file_content: str = ValidValues.ack_headers
    ) -> None:
        """
        Obtains the ack file content and ensures that it matches the expected content (expected content is based
        on the incoming messages).
        """
        actual_ack_file_content = obtain_current_ack_file_content()
        expected_ack_file_content = generate_expected_ack_content(incoming_messages, existing_file_content)
        self.assertEqual(expected_ack_file_content, actual_ack_file_content)

    def test_lambda_handler_main(self):
        """Test lambda handler with consitent ack_file_name and message_template."""
        test_cases = [
            {
                "description": "Multiple messages: all successful",
                "messages": [{"row_id": f"row_{i+1}"} for i in range(10)],
            },
            {
                "description": "Multiple messages: all with diagnostics (failure messages)",
                "messages": [
                    {"row_id": "row_1", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_2", "diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS},
                    {"row_id": "row_3", "diagnostics": DiagnosticsDictionaries.RESOURCE_NOT_FOUND_ERROR},
                ],
            },
            {
                "description": "Multiple messages: mixture of success and failure messages",
                "messages": [
                    {"row_id": "row_1", "imms_id": "TEST_IMMS_ID"},
                    {"row_id": "row_2", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_3", "diagnostics": DiagnosticsDictionaries.CUSTOM_VALIDATION_ERROR},
                    {"row_id": "row_4"},
                    {
                        "row_id": "row_5",
                        "diagnostics": DiagnosticsDictionaries.CUSTOM_VALIDATION_ERROR,
                        "imms_id": "TEST_IMMS_ID",
                    },
                    {"row_id": "row_6", "diagnostics": DiagnosticsDictionaries.CUSTOM_VALIDATION_ERROR},
                    {"row_id": "row_7"},
                    {"row_id": "row_8", "diagnostics": DiagnosticsDictionaries.IDENTIFIER_DUPLICATION_ERROR},
                ],
            },
            {
                "description": "Single row: success",
                "messages": [{"row_id": "row_1"}],
            },
            {
                "description": "Single row: malformed diagnostics info from forwarder",
                "messages": [{"row_id": "row_1", "diagnostics": "SHOULD BE A DICTIONARY, NOT A STRING"}],
            },
        ]

        for test_case in test_cases:
            # Test scenario where there is no existing ack file
            with self.subTest(msg=f"No existing ack file: {test_case['description']}"):
                response = lambda_handler(event=self.generate_event(test_case["messages"]), context={})
                self.assertEqual(response, {"statusCode": 200, "body": '"Lambda function executed successfully!"'})
                self.validate_ack_file_content(test_case["messages"])

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=MOCK_MESSAGE_DETAILS.temp_ack_file_key)

            # Test scenario where there is an existing ack file
            with self.subTest(msg=f"Existing ack file: {test_case['description']}"):
                existing_ack_file_content = test_case.get("existing_ack_file_content", "")
                setup_existing_ack_file(MOCK_MESSAGE_DETAILS.temp_ack_file_key, existing_ack_file_content)
                response = lambda_handler(event=self.generate_event(test_case["messages"]), context={})
                self.assertEqual(response, {"statusCode": 200, "body": '"Lambda function executed successfully!"'})
                self.validate_ack_file_content(test_case["messages"], existing_ack_file_content)

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=MOCK_MESSAGE_DETAILS.temp_ack_file_key)

    def test_lambda_handler_error_scenarios(self):
        """Test that the lambda handler raises appropriate exceptions for malformed event data."""

        test_cases = [
            {
                "description": "Empty event",
                "event": {},
                "expected_message": "No records found in the event",
            },
            {
                "description": "Malformed JSON in SQS body",
                "event": {"Records": [{""}]},
                "expected_message": "Could not load incoming message body",
            },
        ]

        for test_case in test_cases:
            with self.subTest(msg=test_case["description"]):
                with patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose:
                    with self.assertRaises(Exception):
                        lambda_handler(event=test_case["event"], context={})
                error_log = mock_send_log_to_firehose.call_args[0][0]
                self.assertIn(test_case["expected_message"], error_log["diagnostics"])


if __name__ == "__main__":
    unittest.main()
