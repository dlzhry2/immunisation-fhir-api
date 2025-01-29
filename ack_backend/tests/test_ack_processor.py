"""Tests for the ack processor lambda hanlder."""

import unittest
import os
import json
from unittest.mock import patch
from boto3 import client as boto3_client
from moto import mock_s3, mock_firehose
from ack_processor import lambda_handler
from update_ack_file import obtain_current_ack_content, create_ack_data, update_ack_file
from tests.test_utils_for_ack_backend import (
    REGION_NAME,
    ValidValues,
    DiagnosticsDictionaries,
    MOCK_ENVIRONMENT_DICT,
    BucketNames,
    GenericSetUp,
    GenericTearDown,
    MockMessageDetails,
)


s3_client = boto3_client("s3", region_name=REGION_NAME)
firehose_client = boto3_client("firehose", region_name=REGION_NAME)

# Mock message details are used as the default message details for the tests
mock_message_details = MockMessageDetails.rsv_ravs


@patch.dict(os.environ, MOCK_ENVIRONMENT_DICT)
@mock_s3
@mock_firehose
class TestAckProcessor(unittest.TestCase):
    """Tests for the ack processor lambda handler."""

    def setUp(self) -> None:
        GenericSetUp(s3_client, firehose_client)

    def tearDown(self) -> None:
        GenericTearDown(s3_client, firehose_client)

    @staticmethod
    def setup_existing_ack_file(file_key, file_content):
        """Uploads an existing file with the given content."""
        s3_client.put_object(Bucket=BucketNames.DESTINATION, Key=file_key, Body=file_content)

    @staticmethod
    def generate_event(test_messages: list[dict]) -> dict:
        """
        Returns an event where each message in the incoming message body list is based on a standard mock message,
        updated with the details from the corresponsing message in the given test_messages list.
        """
        incoming_message_body = [{**mock_message_details.message, **message} for message in test_messages]
        return {"Records": [{"body": json.dumps(incoming_message_body)}]}

    @staticmethod
    def obtain_current_ack_file_content(ack_file_key: str = mock_message_details.ack_file_key) -> str:
        """Obtains the ack file content from the destination bucket."""
        retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
        return retrieved_object["Body"].read().decode("utf-8")

    @staticmethod
    def generate_expected_ack_file_row(
        success: bool,
        imms_id: str = mock_message_details.imms_id,
        diagnostics: str = None,
        row_id: str = mock_message_details.row_id,
        local_id: str = mock_message_details.local_id,
        created_at_formatted_string: str = mock_message_details.created_at_formatted_string,
    ):
        """Create an ack row, containing the given message details."""
        if success:
            return (
                f"{row_id}|OK|Information|OK|30001|Business|30001|Success|{created_at_formatted_string}|"
                f"|{local_id}|{imms_id}||True"
            )
        else:
            return (
                f"{row_id}|Fatal Error|Fatal|Fatal Error|30002|Business|30002|Business Level Response Value - "
                f"Processing Error|{created_at_formatted_string}||{local_id}|{imms_id}|{diagnostics}|False"
            )

    def generate_sample_existing_ack_content(self) -> str:
        """Returns sample ack file content with a single success row."""
        return ValidValues.ack_headers + self.generate_expected_ack_file_row(success=True)

    def generate_expected_ack_content(
        self, incoming_messages: list[dict], existing_content: str = ValidValues.ack_headers
    ) -> str:
        """Returns the expected_ack_file_content based on the incoming messages"""
        for message in incoming_messages:
            # Determine diagnostics based on the diagnostics value in the incoming message
            diagnostics_dictionary = message.get("diagnostics", {})
            diagnostics = (
                diagnostics_dictionary.get("error_message", "")
                if isinstance(diagnostics_dictionary, dict)
                else "Unable to determine diagnostics issue"
            )

            # Create the ack row based on the incoming message details
            ack_row = self.generate_expected_ack_file_row(
                success=diagnostics is "",
                row_id=message.get("row_id", mock_message_details.row_id),
                created_at_formatted_string=message.get(
                    "created_at_formatted_string", mock_message_details.created_at_formatted_string
                ),
                local_id=message.get("local_id", mock_message_details.local_id),
                imms_id=message.get("imms_id", mock_message_details.imms_id),
                diagnostics=diagnostics,
            )

            existing_content += ack_row + "\n"

        return existing_content

    def validate_ack_file_content(
        self, incoming_messages: list[dict], existing_file_content: str = ValidValues.ack_headers
    ) -> None:
        """
        Obtains the ack file content and ensures that it matches the expected content (expected content is based
        on the incoming messages).
        """
        actual_ack_file_content = self.obtain_current_ack_file_content()
        expected_ack_file_content = self.generate_expected_ack_content(incoming_messages, existing_file_content)
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

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_message_details.ack_file_key)

            # Test scenario where there is an existing ack file
            with self.subTest(msg=f"Existing ack file: {test_case['description']}"):
                existing_ack_file_content = test_case.get("existing_ack_file_content", "")
                self.setup_existing_ack_file(mock_message_details.ack_file_key, existing_ack_file_content)
                response = lambda_handler(event=self.generate_event(test_case["messages"]), context={})
                self.assertEqual(response, {"statusCode": 200, "body": '"Lambda function executed successfully!"'})
                self.validate_ack_file_content(test_case["messages"], existing_ack_file_content)

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_message_details.ack_file_key)

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

    def test_update_ack_file(self):
        """Test that update_ack_file correctly creates the ack file when there was no existing ack file"""

        test_cases = [
            {
                "description": "Single successful row",
                "input_rows": [ValidValues.ack_data_success_dict],
                "expected_rows": [self.generate_expected_ack_file_row(success=True, imms_id="")],
            },
            {
                "description": "With multiple rows - failure and success rows",
                "input_rows": [
                    ValidValues.ack_data_success_dict,
                    {**ValidValues.ack_data_failure_dict, "IMMS_ID": "TEST_IMMS_ID_1"},
                    ValidValues.ack_data_failure_dict,
                    ValidValues.ack_data_failure_dict,
                    {**ValidValues.ack_data_success_dict, "IMMS_ID": "TEST_IMMS_ID_2"},
                ],
                "expected_rows": [
                    self.generate_expected_ack_file_row(success=True, imms_id=""),
                    self.generate_expected_ack_file_row(
                        success=False, imms_id="TEST_IMMS_ID_1", diagnostics="DIAGNOSTICS"
                    ),
                    self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="DIAGNOSTICS"),
                    self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="DIAGNOSTICS"),
                    self.generate_expected_ack_file_row(success=True, imms_id="TEST_IMMS_ID_2"),
                ],
            },
            {
                "description": "Multiple rows With different diagnostics",
                "input_rows": [
                    {**ValidValues.ack_data_failure_dict, "OPERATION_OUTCOME": "Error 1"},
                    {**ValidValues.ack_data_failure_dict, "OPERATION_OUTCOME": "Error 2"},
                    {**ValidValues.ack_data_failure_dict, "OPERATION_OUTCOME": "Error 3"},
                ],
                "expected_rows": [
                    self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="Error 1"),
                    self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="Error 2"),
                    self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="Error 3"),
                ],
            },
        ]

        for test_case in test_cases:
            with self.subTest(test_case["description"]):
                update_ack_file(
                    mock_message_details.file_key,
                    mock_message_details.created_at_formatted_string,
                    test_case["input_rows"],
                )

                actual_ack_file_content = self.obtain_current_ack_file_content()
                expected_ack_file_content = ValidValues.ack_headers + "\n".join(test_case["expected_rows"]) + "\n"
                self.assertEqual(expected_ack_file_content, actual_ack_file_content)

                s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=mock_message_details.ack_file_key)

    def test_update_ack_file_existing(self):
        """Test that update_ack_file correctly updates the ack file when there was an existing ack file"""
        # Mock existing content in the ack file
        existing_content = self.generate_sample_existing_ack_content()
        self.setup_existing_ack_file(mock_message_details.ack_file_key, existing_content)

        ack_data_rows = [ValidValues.ack_data_success_dict, ValidValues.ack_data_failure_dict]
        update_ack_file(mock_message_details.file_key, mock_message_details.created_at_formatted_string, ack_data_rows)

        actual_ack_file_content = self.obtain_current_ack_file_content()
        expected_rows = [
            self.generate_expected_ack_file_row(success=True, imms_id=""),
            self.generate_expected_ack_file_row(success=False, imms_id="", diagnostics="DIAGNOSTICS"),
        ]
        expected_ack_file_content = existing_content + "\n".join(expected_rows) + "\n"
        self.assertEqual(expected_ack_file_content, actual_ack_file_content)

    def test_create_ack_data(self):
        """Test create_ack_data with success and failure cases."""

        success_expected_result = {
            "MESSAGE_HEADER_ID": mock_message_details.row_id,
            "HEADER_RESPONSE_CODE": "OK",
            "ISSUE_SEVERITY": "Information",
            "ISSUE_CODE": "OK",
            "ISSUE_DETAILS_CODE": "30001",
            "RESPONSE_TYPE": "Business",
            "RESPONSE_CODE": "30001",
            "RESPONSE_DISPLAY": "Success",
            "RECEIVED_TIME": mock_message_details.created_at_formatted_string,
            "MAILBOX_FROM": "",
            "LOCAL_ID": mock_message_details.local_id,
            "IMMS_ID": mock_message_details.imms_id,
            "OPERATION_OUTCOME": "",
            "MESSAGE_DELIVERY": True,
        }

        failure_expected_result = {
            "MESSAGE_HEADER_ID": mock_message_details.row_id,
            "HEADER_RESPONSE_CODE": "Fatal Error",
            "ISSUE_SEVERITY": "Fatal",
            "ISSUE_CODE": "Fatal Error",
            "ISSUE_DETAILS_CODE": "30002",
            "RESPONSE_TYPE": "Business",
            "RESPONSE_CODE": "30002",
            "RESPONSE_DISPLAY": "Business Level Response Value - Processing Error",
            "RECEIVED_TIME": mock_message_details.created_at_formatted_string,
            "MAILBOX_FROM": "",
            "LOCAL_ID": mock_message_details.local_id,
            "IMMS_ID": "",
            "OPERATION_OUTCOME": "test diagnostics message",
            "MESSAGE_DELIVERY": False,
        }

        test_cases = [
            {"success": True, "imms_id": mock_message_details.imms_id, "expected_result": success_expected_result},
            {"success": False, "diagnostics": "test diagnostics message", "expected_result": failure_expected_result},
        ]

        for test_case in test_cases:
            with self.subTest(f"success is {test_case['success']}"):
                result = create_ack_data(
                    created_at_formatted_string=mock_message_details.created_at_formatted_string,
                    local_id=mock_message_details.local_id,
                    row_id=mock_message_details.row_id,
                    successful_api_response=test_case["success"],
                    diagnostics=test_case.get("diagnostics"),
                    imms_id=test_case.get("imms_id"),
                )
                self.assertEqual(result, test_case["expected_result"])

    def test_obtain_current_ack_content_file_no_existing(self):
        """Test that when the ack file does not yet exist, obtain_current_ack_content returns the ack headers only."""
        result = obtain_current_ack_content(BucketNames.DESTINATION, mock_message_details.ack_file_key)
        self.assertEqual(result.getvalue(), ValidValues.ack_headers)

    def test_obtain_current_ack_content_file_exists(self):
        """Test that the existing ack file content is retrieved and new rows are added."""
        existing_content = self.generate_sample_existing_ack_content()
        self.setup_existing_ack_file(mock_message_details.ack_file_key, existing_content)
        result = obtain_current_ack_content(BucketNames.DESTINATION, mock_message_details.ack_file_key)
        self.assertEqual(result.getvalue(), existing_content)


if __name__ == "__main__":
    unittest.main()
