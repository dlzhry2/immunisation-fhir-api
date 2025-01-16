"""Tests for the ack processor lambda hanlder."""

import unittest
import os
import json
from unittest.mock import patch
from boto3 import client as boto3_client
from moto import mock_s3, mock_sqs
from ack_processor import lambda_handler
from update_ack_file import obtain_current_ack_content, create_ack_data, update_ack_file
from tests.test_utils_for_ack_backend import (
    REGION_NAME,
    ValidValues,
    MOCK_CREATED_AT_FORMATTED_STRING,
    DiagnosticsDictionaries,
    MOCK_ENVIRONMENT_DICT,
    BucketNames,
    GenericSetUp,
    GenericTearDown,
    MockFileDetails,
    create_ack_row,
)


s3_client = boto3_client("s3", region_name=REGION_NAME)
INVALID_ACTION_FLAG_DIAGNOSTICS = "Invalid ACTION_FLAG - ACTION_FLAG must be 'NEW', 'UPDATE' or 'DELETE'"

mock_file_details = MockFileDetails.rsv_ravs


@patch.dict(os.environ, MOCK_ENVIRONMENT_DICT)
@mock_s3
@mock_sqs
class TestAckProcessor(unittest.TestCase):
    """Tests for the ack processor lambda hanlder."""

    def setUp(self) -> None:
        GenericSetUp(s3_client)

    def tearDown(self) -> None:
        GenericTearDown(s3_client)

    def setup_existing_ack_file(self, file_key, file_content):
        """Uploads an existing file with the given content."""
        s3_client.put_object(Bucket=BucketNames.DESTINATION, Key=file_key, Body=file_content)

    def create_event(self, test_messages):
        """Dynamically create the event for tests with multiple records."""
        incoming_message_body = [{**self.incoming_message_template, **message} for message in test_messages]
        return {"Records": [{"body": json.dumps(incoming_message_body)}]}

    incoming_message_template = {
        "file_key": mock_file_details.file_key,
        "row_id": "123^1",
        "local_id": ValidValues.local_id,
        "operation_requested": "create",
        "imms_id": "",
        "created_at_formatted_string": mock_file_details.created_at_formatted_string,
        "vaccine_type": "RSV",
        "supplier": "RAVS"
    }

    def obtain_current_ack_file_content(self, ack_file_key: str = mock_file_details.ack_file_key) -> str:
        """Obtains the ack file content from the destination bucket."""
        retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
        return retrieved_object["Body"].read().decode("utf-8")

    def validate_ack_file_content(
        self, incoming_messages: list[dict], expected_ack_file_content: str, actual_ack_file_content: str
    ) -> None:
        """
        Validates that rows in actual_ack_file_content match the full row details in expected_ack_file_content
        and appear in the same order as in row_input.
        """
        for message in incoming_messages:
            self.assertIn(f"{message.get('row_id')}|", actual_ack_file_content)

        # Split expected and uploaded content into lines for line-by-line comparison
        expected_lines = expected_ack_file_content.strip().split("\n")
        uploaded_lines = actual_ack_file_content.strip().split("\n")

        # Check each file content the correct amount of lines
        self.assertEqual(len(expected_lines), len(uploaded_lines))

        # Checks each row in expected and actual ack file outputs has exact match and order
        for expected_line, uploaded_line in zip(expected_lines, uploaded_lines):
            self.assertEqual(expected_line, uploaded_line)

    def generate_expected_ack_content(self, incoming_messages: list[dict], base_content: str) -> str:
        """Returns the expected_ack_file_content based on the incoming messages"""
        for row in incoming_messages:
            diagnostics_dictionary = row.get("diagnostics", {})
            diagnostics = (
                diagnostics_dictionary.get("error_message", "")
                if isinstance(diagnostics_dictionary, dict)
                else "Unable to determine diagnostics issue"
            )
            imms_id = row.get("imms_id", "")
            row_id = row.get("row_id")
            ack_row = create_ack_row(
                row_id, mock_file_details.created_at_formatted_string, "111^222", imms_id, diagnostics
            )
            base_content += ack_row + "\n"
        return base_content

    def test_lambda_handler_main(self):
        """Test lambda handler with dynamic ack_file_name and consistent row_template."""
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

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                with (patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose,):
                    response = lambda_handler(event=self.create_event(case["messages"]), context={})

                self.assertEqual(response, {"statusCode": 200, "body": '"Lambda function executed successfully!"'})

                actual_ack_file_content = self.obtain_current_ack_file_content()
                expected_ack_file_content = self.generate_expected_ack_content(
                    case["messages"], base_content=ValidValues.ack_headers
                )
                self.validate_ack_file_content(case["messages"], expected_ack_file_content, actual_ack_file_content)

                mock_send_log_to_firehose.assert_called()

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_file_details.ack_file_key)

    def test_lambda_handler_existing(self):
        """Test lambda handler with dynamic ack_file_name and consistent row_template with an already existing
        ack file with content."""
        test_cases = [
            {
                "description": "Multiples messages: all failure messages",
                "messages": [
                    {"row_id": "row_1", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_2", "diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS},
                    {"row_id": "row_3", "diagnostics": DiagnosticsDictionaries.RESOURCE_NOT_FOUND_ERROR},
                ],
            },
            {
                "description": "Multiples messages: mixture of success and failure messages",
                "messages": [
                    {"row_id": "row_4", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_5"},
                    {"row_id": "row_6"},
                    {"row_id": "row_7", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_8", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_9", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                ],
            },
            {
                "description": "Single message: success",
                "messages": [{"row_id": "row_412"}, {"row_id": "row_413"}],
            },
        ]

        for case in test_cases:
            with self.subTest(msg=case["description"]):
                self.setup_existing_ack_file(mock_file_details.ack_file_key, ValidValues.existing_ack_file_content)

                with (patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose,):
                    response = lambda_handler(event=self.create_event(case["messages"]), context={})

                self.assertEqual(response, {"statusCode": 200, "body": '"Lambda function executed successfully!"'})

                actual_ack_file_content = self.obtain_current_ack_file_content()
                expected_ack_file_content = self.generate_expected_ack_content(
                    case["messages"], ValidValues.existing_ack_file_content
                )
                self.assertIn(ValidValues.existing_ack_file_content, actual_ack_file_content)
                self.validate_ack_file_content(case["messages"], expected_ack_file_content, actual_ack_file_content)

                mock_send_log_to_firehose.assert_called()

                # Tear down after each case to ensure independence of the test cases
                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_file_details.ack_file_key)

    def test_update_ack_file(self):
        """Test creating ack file with and without diagnostics"""

        test_cases = [
            {
                "description": "Single successful row",
                "input_rows": [ValidValues.create_ack_data_successful_row],
                "expected_rows": [
                    ValidValues.update_ack_file_successful_row_no_immsid,
                ],
            },
            {
                "description": "With multiple rows - failure and success rows",
                "input_rows": [
                    ValidValues.create_ack_data_successful_row,
                    {**ValidValues.create_ack_data_failure_row, "IMMS_ID": "TEST_IMMS_ID"},
                    ValidValues.create_ack_data_failure_row,
                    ValidValues.create_ack_data_failure_row,
                    {**ValidValues.create_ack_data_successful_row, "IMMS_ID": "TEST_IMMS_ID"},
                ],
                "expected_rows": [
                    ValidValues.update_ack_file_successful_row_no_immsid,
                    ValidValues.update_ack_file_failure_row_immsid,
                    ValidValues.update_ack_file_failure_row_no_immsid,
                    ValidValues.update_ack_file_failure_row_no_immsid,
                    ValidValues.update_ack_file_successful_row_immsid,
                ],
            },
            {
                "description": "Multiple rows With different diagnostics",
                "input_rows": [
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 1"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 2"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 3"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 4"},
                ],
                "expected_rows": [
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 1"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 2"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 3"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 4"),
                ],
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                update_ack_file(
                    mock_file_details.file_key, mock_file_details.created_at_formatted_string, case["input_rows"]
                )

                for expected_row in case["expected_rows"]:
                    self.assertIn(expected_row, self.obtain_current_ack_file_content())

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_file_details.ack_file_key)

    def test_update_ack_file_existing(self):
        """Test appending new rows to an existing ack file."""
        # Mock existing content in the ack file
        existing_content = ValidValues.existing_ack_file_content
        self.setup_existing_ack_file(mock_file_details.ack_file_key, existing_content)

        ack_data_rows = [ValidValues.create_ack_data_successful_row, ValidValues.create_ack_data_failure_row]
        update_ack_file(mock_file_details.file_key, MOCK_CREATED_AT_FORMATTED_STRING, ack_data_rows)

        actual_ack_file_content = self.obtain_current_ack_file_content(mock_file_details.ack_file_key)
        self.assertIn(existing_content, actual_ack_file_content)
        self.assertIn(ValidValues.update_ack_file_successful_row_no_immsid, actual_ack_file_content)
        self.assertIn(ValidValues.update_ack_file_failure_row_no_immsid, actual_ack_file_content)

        s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_file_details.ack_file_key)

    def test_create_ack_data(self):
        """Test create_ack_data with success and failure cases."""

        test_cases = [
            {
                "description": "Success row",
                "created_at_formatted_string": mock_file_details.created_at_formatted_string,
                "local_id": "local123",
                "row_id": "row123",
                "successful_api_response": True,
                "diagnostics": None,
                "imms_id": "imms123",
                "expected_base": ValidValues.create_ack_data_successful_row,
            },
            {
                "description": "Failure row",
                "created_at_formatted_string": "20241115T13435501",
                "local_id": "local4556",
                "row_id": "row456",
                "successful_api_response": False,
                "diagnostics": "Some error occurred",
                "imms_id": "imms456",
                "expected_base": ValidValues.create_ack_data_failure_row,
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                result = create_ack_data(
                    created_at_formatted_string=case["created_at_formatted_string"],
                    local_id=case["local_id"],
                    row_id=case["row_id"],
                    successful_api_response=case["successful_api_response"],
                    diagnostics=case["diagnostics"],
                    imms_id=case["imms_id"],
                )

                expected_result = {
                    **case["expected_base"],
                    "MESSAGE_HEADER_ID": case["row_id"],
                    "RECEIVED_TIME": case["created_at_formatted_string"],
                    "LOCAL_ID": case["local_id"],
                    "IMMS_ID": case["imms_id"] or "",
                    "OPERATION_OUTCOME": case["diagnostics"] or "",
                }
                self.assertEqual(result, expected_result)

    def test_obtain_current_ack_content_file_no_existing(self):
        """Test that when the ack file does not yet exist, obtain_current_ack_content returns the ack headers only."""
        result = obtain_current_ack_content(BucketNames.DESTINATION, mock_file_details.ack_file_key)
        self.assertEqual(result.getvalue(), ValidValues.ack_headers)

    def test_obtain_current_ack_content_file_exists(self):
        """Test that the existing ack file content is retrieved and new rows are added."""
        # TODO: This test doesn't check that new rows are added, but this funtion doesn't add them.
        # Should there be another test?
        existing_content = ValidValues.existing_ack_file_content
        self.setup_existing_ack_file(mock_file_details.ack_file_key, existing_content)

        result = obtain_current_ack_content(BucketNames.DESTINATION, mock_file_details.ack_file_key)

        self.assertEqual(result.getvalue(), existing_content)

        s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_file_details.ack_file_key)

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
        # TODO: What was below meant to be testing?
        # mock_update_ack_file.side_effect = Exception("Simulated create_ack_data error")

        for scenario in test_cases:
            with self.subTest(msg=scenario["description"]):
                with patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose:
                    with self.assertRaises(Exception):
                        lambda_handler(event=scenario["event"], context={})

                error_log = mock_send_log_to_firehose.call_args[0][0]
                self.assertIn(scenario["expected_message"], error_log["diagnostics"])


if __name__ == "__main__":
    unittest.main()
