import unittest
from moto import mock_s3, mock_sqs
import os
import json
from boto3 import client as boto3_client
from unittest.mock import patch
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
)
from copy import deepcopy
import uuid


s3_client = boto3_client("s3", region_name=REGION_NAME)
local_id = "111^222"
INVALID_ACTION_FLAG_DIAGNOSTICS = "Invalid ACTION_FLAG - ACTION_FLAG must be 'NEW', 'UPDATE' or 'DELETE'"

mock_file = MockFileDetails.flu_emis
ack_file_key = mock_file.ack_file_key


@patch.dict(os.environ, MOCK_ENVIRONMENT_DICT)
@mock_s3
@mock_sqs
class TestAckProcessor(unittest.TestCase):

    def setUp(self) -> None:
        GenericSetUp(s3_client)

    def tearDown(self) -> None:
        GenericTearDown(s3_client)

    def setup_existing_ack_file(self, file_key, file_content):
        """Uploads an existing file with the given content."""
        s3_client.put_object(Bucket=BucketNames.DESTINATION, Key=file_key, Body=file_content)

    def create_event(self, test_data):
        """
        Dynamically create the event for tests with multiple records.
        """
        rows = []
        for test_case_row in test_data["rows"]:
            row = self.row_template.copy()
            row.update(test_case_row)
            rows.append(row)
        return {"Records": [{"body": json.dumps(rows)}]}

    row_template = {
        "file_key": mock_file.file_key,
        "row_id": "123^1",
        "local_id": ValidValues.local_id,
        "operation_requested": "create",
        "imms_id": "",
        "created_at_formatted_string": mock_file.created_at_formatted_string,
    }

    def ack_row_order(self, row_input, expected_ack_file_content, actual_ack_file_content):
        """
        Validates that rows in actual_ack_file_content match the full row details in expected_ack_file_content
        and appear in the same order as in row_input.
            expected_ack_file_content (str): Full expected content of the ACK file from test.
            actual_ack_file_content (str): Actual content uploaded to the ACK file.
        """

        for row in row_input:
            row_id = row.get("row_id")
            self.assertIn(f"{row_id}|", actual_ack_file_content)

        # Split expected and uploaded content into lines for line-by-line comparison
        expected_lines = expected_ack_file_content.strip().split("\n")
        uploaded_lines = actual_ack_file_content.strip().split("\n")

        # Check each file content the correct amount of lines
        self.assertEqual(len(expected_lines), len(uploaded_lines))

        # Checks each row in expected and actual ack file outputs has exact match and order
        for i, (expected_line, uploaded_line) in enumerate(zip(expected_lines, uploaded_lines)):
            self.assertEqual(expected_line, uploaded_line)

    def create_expected_ack_content(self, row_input, actual_ack_file_content, expected_ack_file_content):
        """creates test ack rows from using a list containing multiple rows"""
        for row in row_input:
            diagnostics_dictionary = row.get("diagnostics", {})
            diagnostics = (
                diagnostics_dictionary.get("error_message", "")
                if isinstance(diagnostics_dictionary, dict)
                else "Unable to determine diagnostics issue"
            )
            imms_id = row.get("imms_id", "")
            row_id = row.get("row_id")
            if diagnostics:
                ack_row = (
                    f"{row_id}|Fatal Error|Fatal|Fatal Error|30002|Business|30002|Business Level "
                    f"Response Value - Processing Error|{mock_file.created_at_formatted_string}||111^222|{imms_id}|{diagnostics}|False"
                )
            else:
                ack_row = (
                    f"{row_id}|OK|Information|OK|30001|Business|30001|Success|{mock_file.created_at_formatted_string}|"
                    f"|111^222|{imms_id}||True"
                )

            expected_ack_file_content += ack_row + "\n"

        self.assertEqual(actual_ack_file_content, expected_ack_file_content)
        self.ack_row_order(row_input, expected_ack_file_content, actual_ack_file_content)

    def generate_file_names(self):
        """Generates dynamic file names
        Returns:
            dict: A dictionary containing `file_key_existing`, `ack_file_name`, and `row_template`."""
        file_key_existing = f"COVID19_Vaccinations_v5_DPSREDUCED_{uuid.uuid4().hex}.csv"
        ack_file_name = (
            f"forwardedFile/{file_key_existing.replace('.csv', f'_BusAck_{mock_file.created_at_formatted_string}.csv')}"
        )

        row_template = self.row_template.copy()
        row_template.update({"file_key": file_key_existing})

        return {
            "file_key_existing": file_key_existing,
            "ack_file_name": ack_file_name,
            "row_template": row_template,
        }

    @patch("logging_decorators.send_log_to_firehose")
    def test_lambda_handler_main(self, mock_send_log_to_firehose):
        """Test lambda handler with dynamic ack_file_name and consistent row_template."""
        existing_content = ValidValues.test_ack_header

        test_cases = [
            {
                "description": "10 success rows (No diagnostics)",
                "rows": [{"row_id": f"row_{i+1}"} for i in range(10)],
            },
            {
                "description": "SQS event with multiple errors",
                "rows": [
                    {"row_id": "row_1", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_2", "diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS},
                    {"row_id": "row_3", "diagnostics": DiagnosticsDictionaries.RESOURCE_NOT_FOUND_ERROR},
                ],
            },
            {
                "description": "Multiple row processing from SQS event - mixture of success and failure rows",
                "rows": [
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
                "description": "1 success row (No diagnostics)",
                "rows": [{"row_id": "row_1"}],
            },
            {
                "description": "1 row with malformed diagnostics info from forwarder",
                "rows": [{"row_id": "row_1", "diagnostics": "SHOULD BE A DICTIONARY, NOT A STRING"}],
            },
        ]

        with patch("update_ack_file.s3_client", s3_client):
            for case in test_cases:
                with self.subTest(msg=case["description"]):
                    # Generate unique file names and set up the S3 file
                    file_info = self.generate_file_names()

                    test_data = {"rows": [{**file_info["row_template"], **row} for row in case["rows"]]}

                    event = self.create_event(test_data)

                    response = lambda_handler(event=event, context={})

                    self.assertEqual(response["statusCode"], 200)
                    self.assertEqual(response["body"], '"Lambda function executed successfully!"')

                    retrieved_object = s3_client.get_object(
                        Bucket=BucketNames.DESTINATION, Key=file_info["ack_file_name"]
                    )
                    actual_ack_file_content = retrieved_object["Body"].read().decode("utf-8")

                    self.create_expected_ack_content(test_data["rows"], actual_ack_file_content, existing_content)

                    mock_send_log_to_firehose.assert_called()

                    s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=file_info["ack_file_name"])

    @patch("logging_decorators.send_log_to_firehose")
    def test_lambda_handler_existing(self, mock_send_log_to_firehose):
        """Test lambda handler with dynamic ack_file_name and consistent row_template with an already existing
        ack file with content."""

        existing_content = ValidValues.existing_ack_file_content

        test_cases = [
            {
                "description": "SQS event with multiple errors",
                "rows": [
                    {"row_id": "row_1", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_2", "diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS},
                    {"row_id": "row_3", "diagnostics": DiagnosticsDictionaries.RESOURCE_NOT_FOUND_ERROR},
                ],
            },
            {
                "description": "SQS event with mixed success and failure rows",
                "rows": [
                    {"row_id": "row_4", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_5"},
                    {"row_id": "row_6"},
                    {"row_id": "row_7", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_8", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                    {"row_id": "row_9", "diagnostics": DiagnosticsDictionaries.UNIQUE_ID_MISSING},
                ],
            },
            {
                "description": "Success rows (No diagnostics)",
                "rows": [{"row_id": "row_412"}, {"row_id": "row_413"}],
            },
        ]

        with patch("update_ack_file.s3_client", s3_client):
            for case in test_cases:
                with self.subTest(msg=case["description"]):
                    # Generate unique file names and set up the S3 file
                    file_info = self.generate_file_names()
                    self.setup_existing_ack_file(file_info["ack_file_name"], existing_content)

                    test_data = {"rows": [{**file_info["row_template"], **row} for row in case["rows"]]}

                    event = self.create_event(test_data)

                    response = lambda_handler(event=event, context={})

                    self.assertEqual(response["statusCode"], 200)
                    self.assertEqual(response["body"], '"Lambda function executed successfully!"')

                    retrieved_object = s3_client.get_object(
                        Bucket=BucketNames.DESTINATION, Key=file_info["ack_file_name"]
                    )
                    actual_ack_file_content = retrieved_object["Body"].read().decode("utf-8")

                    self.assertIn(
                        f"123^5|OK|Information|OK|30001|Business|30001|Success|{mock_file.created_at_formatted_string}||999^TEST|||True",
                        actual_ack_file_content,
                    )
                    self.assertIn(ValidValues.test_ack_header, actual_ack_file_content)

                    self.create_expected_ack_content(test_data["rows"], actual_ack_file_content, existing_content)

                    mock_send_log_to_firehose.assert_called()

                    s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=file_info["ack_file_name"])

    def test_update_ack_file(self):
        """Test creating ack file with and without diagnostics"""

        test_cases = [
            {
                "description": "Single successful row",
                "input_row": [ValidValues.create_ack_data_successful_row],
                "expected_row": [
                    ValidValues.update_ack_file_successful_row_no_immsid,
                ],
            },
            {
                "description": "With multiple rows - failure and success rows",
                "input_row": [
                    ValidValues.create_ack_data_successful_row,
                    {**ValidValues.create_ack_data_failure_row, "IMMS_ID": "TEST_IMMS_ID"},
                    ValidValues.create_ack_data_failure_row,
                    ValidValues.create_ack_data_failure_row,
                    {**ValidValues.create_ack_data_successful_row, "IMMS_ID": "TEST_IMMS_ID"},
                ],
                "expected_row": [
                    ValidValues.update_ack_file_successful_row_no_immsid,
                    ValidValues.update_ack_file_failure_row_immsid,
                    ValidValues.update_ack_file_failure_row_no_immsid,
                    ValidValues.update_ack_file_failure_row_no_immsid,
                    ValidValues.update_ack_file_successful_row_immsid,
                ],
            },
            {
                "description": "Multiple rows With different diagnostics",
                "input_row": [
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 1"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 2"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 3"},
                    {**ValidValues.create_ack_data_failure_row, "OPERATION_OUTCOME": "Error 4"},
                ],
                "expected_row": [
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 1"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 2"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 3"),
                    ValidValues.update_ack_file_failure_row_no_immsid.replace("Error_value", "Error 4"),
                ],
            },
        ]

        with patch("update_ack_file.s3_client", s3_client):
            for case in test_cases:
                with self.subTest(deepcopy(case["description"])):
                    ack_data_rows_with_id = []
                    for row in deepcopy(case["input_row"]):
                        ack_data_rows_with_id.append(row)
                    update_ack_file(mock_file.file_key, mock_file.created_at_formatted_string, ack_data_rows_with_id)
                    expected_ack_file_key = mock_file.ack_file_key
                    objects = s3_client.list_objects_v2(Bucket=BucketNames.DESTINATION)
                    self.assertIn(expected_ack_file_key, [obj["Key"] for obj in objects.get("Contents", [])])
                    retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
                    retrieved_body = retrieved_object["Body"].read().decode("utf-8")

                    for expected_row in deepcopy(case["expected_row"]):
                        self.assertIn(expected_row, retrieved_body)

                    s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)

    def test_update_ack_file_existing(self):
        """Test appending new rows to an existing ack file."""

        # Mock existing content in the ack file
        existing_content = ValidValues.existing_ack_file_content

        file_key = "RSV_Vaccinations_v5_TEST_20240905T13005922.csv"
        ack_file_key = f"forwardedFile/RSV_Vaccinations_v5_TEST_20240905T13005922_BusAck_{mock_file.created_at_formatted_string}.csv"
        ack_data_rows = [
            ValidValues.create_ack_data_successful_row,
            ValidValues.create_ack_data_failure_row,
        ]

        self.setup_existing_ack_file(ack_file_key, existing_content)
        retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
        retrieved_body = retrieved_object["Body"].read().decode("utf-8")

        with patch("update_ack_file.s3_client", s3_client):
            update_ack_file(file_key, MOCK_CREATED_AT_FORMATTED_STRING, ack_data_rows)
            retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
            retrieved_body = retrieved_object["Body"].read().decode("utf-8")

            self.assertIn(
                f"123^5|OK|Information|OK|30001|Business|30001|Success|{mock_file.created_at_formatted_string}||999^TEST|||True",
                retrieved_body,
            )

            # Check new rows added to file
            self.assertIn("123^1|OK|", retrieved_body)
            self.assertIn("123^1|Fatal Error|", retrieved_body)

            objects = s3_client.list_objects_v2(Bucket=BucketNames.DESTINATION)
            self.assertIn(ack_file_key, [obj["Key"] for obj in objects.get("Contents", [])])

            s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)

    def test_create_ack_data(self):
        """Test create_ack_data with success and failure cases."""

        test_cases = [
            {
                "description": "Success row",
                "created_at_formatted_string": mock_file.created_at_formatted_string,
                "local_id": "local123",
                "row_id": "row456",
                "successful_api_response": True,
                "diagnostics": None,
                "imms_id": "imms789",
                "expected_base": ValidValues.create_ack_data_successful_row,
            },
            {
                "description": "Failure row",
                "created_at_formatted_string": "20241115T13435501",
                "local_id": "local123",
                "row_id": "row456",
                "successful_api_response": False,
                "diagnostics": "Some error occurred",
                "imms_id": "imms789",
                "expected_base": ValidValues.create_ack_data_failure_row,
            },
        ]

        for case in test_cases:
            with self.subTest(case["description"]):
                expected_result = case["expected_base"].copy()
                expected_result.update(
                    {
                        "MESSAGE_HEADER_ID": case["row_id"],
                        "RECEIVED_TIME": case["created_at_formatted_string"],
                        "LOCAL_ID": case["local_id"],
                        "IMMS_ID": case["imms_id"] or "",
                        "OPERATION_OUTCOME": case["diagnostics"] or "",
                    }
                )

                result = create_ack_data(
                    created_at_formatted_string=case["created_at_formatted_string"],
                    local_id=case["local_id"],
                    row_id=case["row_id"],
                    successful_api_response=case["successful_api_response"],
                    diagnostics=case["diagnostics"],
                    imms_id=case["imms_id"],
                )

                self.assertEqual(result, expected_result)

    def test_obtain_current_ack_content_file_no_existing(self):
        """Test obtain current ack content when there a file does not already exist."""
        ACK_KEY = "forwardedFile/COVID19_Vaccinations_v5_YGM41_20240909T13005902_BusAck_20241115T13454555.csv"
        with patch("update_ack_file.s3_client", s3_client):
            result = obtain_current_ack_content(BucketNames.DESTINATION, ACK_KEY)
        self.assertEqual(result.getvalue(), ValidValues.test_ack_header)

    def test_obtain_current_ack_content_file_exists(self):
        """Test that the existing ack file content is retrieved and new rows are added."""
        existing_content = ValidValues.existing_ack_file_content
        self.setup_existing_ack_file(ack_file_key, existing_content)

        with patch("update_ack_file.s3_client", s3_client):
            result = obtain_current_ack_content(BucketNames.DESTINATION, ack_file_key)
            self.assertIn(existing_content, result.getvalue())
            self.assertEqual(result.getvalue(), existing_content)

            retrieved_object = s3_client.get_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)
            retrieved_body = retrieved_object["Body"].read().decode("utf-8")
            self.assertEqual(retrieved_body, existing_content)

            objects = s3_client.list_objects_v2(Bucket=BucketNames.DESTINATION)
            self.assertIn(ack_file_key, [obj["Key"] for obj in objects.get("Contents", [])])

            s3_client.delete_object(Bucket=BucketNames.DESTINATION, Key=ack_file_key)

    @patch("logging_decorators.send_log_to_firehose")
    @patch("update_ack_file.create_ack_data")
    @patch("update_ack_file.update_ack_file")
    def test_lambda_handler_error_scenarios(
        self, mock_update_ack_file, mock_create_ack_data, mock_send_log_to_firehose
    ):

        with self.subTest("No records in the event"):
            with self.assertRaises(Exception):
                lambda_handler(event={}, context={})

            mock_send_log_to_firehose.assert_called()
            error_log = mock_send_log_to_firehose.call_args[0][0]
            self.assertIn("No records found in the event", error_log["diagnostics"])
            mock_send_log_to_firehose.reset_mock()

        test_cases = [
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
                with self.assertRaises(Exception):
                    lambda_handler(event=scenario["event"], context={})

                mock_send_log_to_firehose.assert_called()
                error_log = mock_send_log_to_firehose.call_args[0][0]
                self.assertIn(scenario["expected_message"], error_log["diagnostics"])
                mock_send_log_to_firehose.reset_mock()


if __name__ == "__main__":
    unittest.main()
