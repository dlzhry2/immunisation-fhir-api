import unittest
from unittest.mock import patch, call
import json
import copy
from contextlib import ExitStack
from moto import mock_s3
from boto3 import client as boto3_client
from src.ack_processor import lambda_handler
from tests.test_utils_for_ack_backend import (
    ValidValues,
    InvalidValues,
    DiagnosticsDictionaries,
    GenericSetUp,
    GenericTearDown,
    MOCK_ENVIRONMENT_DICT,
    ValidValues,
)

s3_client = boto3_client("s3")


@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
@mock_s3
class TestSplunkFunctionInfo(unittest.TestCase):

    message_body_base = {"Records": [{"body": json.dumps([ValidValues.DPSFULL_ack_processor_input])}]}
    message_body_two_base = {
        "Records": [
            {"body": json.dumps([ValidValues.DPSFULL_ack_processor_input, ValidValues.DPSFULL_ack_processor_input])}
        ]
    }

    lambda_handler_success_expected_log = {
        "function_name": "ack_processor_lambda_handler",
        "date_time": ValidValues.fixed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "success",
        "statusCode": 200,
        "message": "Lambda function executed successfully!",
    }

    lambda_handler_failure_expected_log = {
        "function_name": "ack_processor_lambda_handler",
        "date_time": ValidValues.fixed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "fail",
        "statusCode": 500,
        "diagnostics": "DIAGNOSTICS MESSAGE",
    }

    def run(self, result=None):
        """
        This method is run by Unittest, and is being utilised here to apply common patches to all of the tests in the
        class. Using ExitStack allows multiple patches to be applied, whilst ensuring that the mocks are cleaned up
        after the test has run.
        """
        # Set up common patches to be applied to all tests in the class.
        # These patches can be overridden in individual tests.
        common_patches = [
            # NOTE: python3.10/logging/__init__.py file, which is run when logger.info is called, makes a call to
            # time.time. This interferes with patching of the time.time function in these tests.
            # The logging_decorator.logger is patched individually in each test to allow for assertions to be made.
            # Any uses of the logger in other files will confound the tests and should be patched here.
            patch("update_ack_file.logger"),
            # Time is incremented by 1.0 for each call to time.time for ease of testing
            patch("logging_decorators.time.time", side_effect=[1.0 + i for i in range(0, 20, 1)]),
        ]

        # Set up the ExitStack. Note that patches need to be explicitly started so that they will be applied even when
        # only running one individual test.
        with ExitStack() as stack:
            # datetime.now is patched to return a fixed datetime for ease of testing
            mock_datetime = patch("logging_decorators.datetime").start()
            mock_datetime.now.return_value = ValidValues.fixed_datetime
            stack.enter_context(patch("logging_decorators.datetime", mock_datetime))

            for common_patch in common_patches:
                common_patch.start()
                stack.enter_context(common_patch)

            super().run(result)

    def setUp(self):
        GenericSetUp(s3_client)

    def tearDown(self):
        GenericTearDown(s3_client)

    def create_event(self, test_messages):
        """Dynamically create the event for tests with multiple records."""
        incoming_message_body = [{**self.incoming_message_template, **message} for message in test_messages]
        return {"Records": [{"body": json.dumps(incoming_message_body)}]}

    incoming_message_template = ValidValues.DPSFULL_ack_processor_input

    def extract_log_json(self, log_entry):
        """Extracts JSON from log entry."""
        json_start = log_entry.find("{")
        json_str = log_entry[json_start:]
        return json.loads(json_str)

    def extract_all_call_args_for_logger_info(self, mock_logger):
        """Extracts all arguments for logger.info."""
        return [args[0] for args, _ in mock_logger.info.call_args_list]

    def extract_all_call_args_for_logger_error(self, mock_logger):
        """Extracts all arguments for logger.info."""
        return [args[0] for args, _ in mock_logger.error.call_args_list]

    def test_splunk_logging_successful_rows(self):
        """Tests a single object in the body of the event"""

        for operation in ["CREATE", "UPDATE", "DELETE"]:
            with (
                patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose,
                patch("logging_decorators.logger") as mock_logger,
            ):
                result = lambda_handler(event=self.create_event([{"operation_requested": operation}]), context={})

            self.assertEqual(result, {"statusCode": 200, "body": json.dumps("Lambda function executed successfully!")})

            expected_first_log_data = {
                **ValidValues.DPSFULL_expected_log_value,
                "operation_requested": operation,
                "time_taken": "1.0s",  # Start and end times are mocked as 1.0 and 2.0 respectively
            }

            expected_second_log_data = {
                **self.lambda_handler_success_expected_log,
                "time_taken": "3.0s",  # Start and end times are mocked as 1.0 and 4.0 respectively
            }

            all_logger_info_call_args = self.extract_all_call_args_for_logger_info(mock_logger)
            first_logger_info_call_args = json.loads(all_logger_info_call_args[0])
            second_logger_info_call_args = json.loads(all_logger_info_call_args[1])
            self.assertEqual(first_logger_info_call_args, expected_first_log_data)
            self.assertEqual(second_logger_info_call_args, expected_second_log_data)

            mock_send_log_to_firehose.assert_has_calls([call(expected_first_log_data), call(expected_second_log_data)])

    def test_splunk_logging_missing_data(self):
        """Tests missing key values in the body of the event"""

        with (
            patch("logging_decorators.send_log_to_firehose") as mock_send_log_to_firehose,
            patch("logging_decorators.logger") as mock_logger,
        ):
            message_body = {"Records": [{"body": json.dumps([{"": "456"}])}]}

            context = {}

            with self.assertRaises(Exception):
                lambda_handler(message_body, context)

            expected_first_log_data = {
                **InvalidValues.Logging_with_no_values,
                "time_taken": "1.0s",  # Start and end times are mocked as 1.0 and 2.0 respectively
            }

            # expected_second_log_data = {
            #     **self.lambda_handler_success_expected_log,
            #     "time_taken": "3.0s",  # Start and end times are mocked as 1.0 and 4.0 respectively
            # }

            all_logger_info_call_args = self.extract_all_call_args_for_logger_info(mock_logger)
            first_logger_info_call_args = json.loads(all_logger_info_call_args[0])
            print(first_logger_info_call_args)
            # second_logger_info_call_args = json.loads(all_logger_info_call_args[1])
            self.assertEqual(first_logger_info_call_args, expected_first_log_data)
            # self.assertEqual(second_logger_info_call_args, expected_second_log_data)

            mock_send_log_to_firehose.assert_has_calls([call(expected_first_log_data)])

    @patch("logging_decorators.send_log_to_firehose")
    @patch("time.time")
    @patch("logging_decorators.datetime")
    def test_splunk_logging_statuscode_diagnostics(
        self,
        mock_datetime,
        mock_time,
        mock_send_log_to_firehose,
    ):
        """'Tests the correct codes are returned for diagnostics"""

        mock_datetime.now.return_value = ValidValues.fixed_datetime
        mock_time.side_effect = [100000.0 + i for i in range(0, 48, 1)]

        operations = [
            {"diagnostics": DiagnosticsDictionaries.RESOURCE_FOUND_ERROR, "expected_code": 409},
            {"diagnostics": DiagnosticsDictionaries.RESOURCE_NOT_FOUND_ERROR, "expected_code": 404},
            {"diagnostics": DiagnosticsDictionaries.MESSAGE_NOT_SUCCESSFUL_ERROR, "expected_code": 500},
            {"diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS, "expected_code": 403},
            {"diagnostics": DiagnosticsDictionaries.IDENTIFIER_DUPLICATION_ERROR, "expected_code": 422},
            {"diagnostics": DiagnosticsDictionaries.UNHANDLED_ERROR, "expected_code": 500},
        ]

        for operation in operations:
            with self.assertLogs(level="INFO") as log:
                message_body = copy.deepcopy(self.message_body_base)

                for record in message_body["Records"]:
                    body_data = json.loads(record["body"])
                    for item in body_data:
                        item["diagnostics"] = operation["diagnostics"]
                    record["body"] = json.dumps(body_data)
                context = {}

                result = lambda_handler(message_body, context)
                self.assertIn("200", str(result["statusCode"]))
                self.assertGreater(len(log.output), 0)

                log_json = self.extract_log_json(log.output[0])
                expected_values = copy.deepcopy(ValidValues.DPSFULL_expected_log_value)
                expected_values["diagnostics"] = operation["diagnostics"].get("error_message")
                expected_values["statusCode"] = operation["expected_code"]
                expected_values["status"] = "fail"
                expected_values["time_taken"] = "1.0s"

                for key, expected in expected_values.items():
                    self.assertEqual(log_json[key], expected)

                mock_send_log_to_firehose.assert_has_calls([call(log_json)])
                mock_send_log_to_firehose.reset_mock()

    @patch("update_ack_file.upload_ack_file")
    @patch("update_ack_file.obtain_current_ack_content")
    @patch("ack_processor.create_ack_data")
    @patch("ack_processor.update_ack_file")
    @patch("logging_decorators.send_log_to_firehose")
    @patch("time.time")
    @patch("logging_decorators.datetime")
    def test_splunk_logging_multiple_rows(
        self,
        mock_datetime,
        mock_time,
        mock_send_log_to_firehose,
        mock_update_ack_file,
        mock_create_ack_data,
        mock_obtain_current_ack_content,
        mock_upload_ack_file,
    ):
        """Tests logging for multiple objects in the body of the event"""
        mock_datetime.now.return_value = ValidValues.fixed_datetime
        mock_time.side_effect = [100000.0 + i for i in range(0, 12, 1)]
        mock_create_ack_data.return_value = None
        mock_update_ack_file.return_value = {}

        with self.assertLogs(level="INFO") as log:
            message_body = copy.deepcopy(self.message_body_two_base)
            for record in message_body["Records"]:
                body_data = json.loads(record["body"])
                record["body"] = json.dumps(body_data)

            context = {}
            result = lambda_handler(message_body, context)
            self.assertIn("200", str(result["statusCode"]))

            self.assertEqual(len(log.output), 3)
            log_entries = [self.extract_log_json(entry) for entry in log.output]

            expected_entries = [
                copy.deepcopy(ValidValues.DPSFULL_expected_log_value),
                copy.deepcopy(ValidValues.DPSFULL_expected_log_value),
            ]

            for idx, entry in enumerate(log_entries[:2]):
                for key, expected in expected_entries[idx].items():
                    self.assertEqual(entry[key], expected)

            self.assertEqual(mock_send_log_to_firehose.call_count, 3)
            mock_send_log_to_firehose.reset_mock()

    @patch("update_ack_file.upload_ack_file")
    @patch("update_ack_file.obtain_current_ack_content")
    @patch("ack_processor.create_ack_data")
    @patch("ack_processor.update_ack_file")
    @patch("logging_decorators.send_log_to_firehose")
    @patch("time.time")
    @patch("logging_decorators.datetime")
    def test_splunk_logging_multiple_with_diagnostics(
        self,
        mock_datetime,
        mock_time,
        mock_send_log_to_firehose,
        mock_update_ack_file,
        mock_create_ack_data,
        mock_obtain_current_ack_content,
        mock_upload_ack_file,
    ):
        """Tests logging for multiple objects in the body of the event with diagnostics"""

        mock_datetime.now.return_value = ValidValues.fixed_datetime
        mock_time.side_effect = [100000.0 + i for i in range(27)]

        mock_create_ack_data.return_value = None
        mock_update_ack_file.return_value = {}
        operations = [
            {"operation_request": "CREATE", "diagnostics": DiagnosticsDictionaries.RESOURCE_FOUND_ERROR},
            {"operation_request": "UPDATE", "diagnostics": DiagnosticsDictionaries.MESSAGE_NOT_SUCCESSFUL_ERROR},
            {"operation_request": "DELETE", "diagnostics": DiagnosticsDictionaries.NO_PERMISSIONS},
        ]

        for op in operations:
            with self.assertLogs(level="INFO") as log:
                message_body = copy.deepcopy(self.message_body_two_base)

                for record in message_body["Records"]:
                    body_data = json.loads(record["body"])
                    for item in body_data:
                        item["operation_requested"] = op["operation_request"]
                        item["diagnostics"] = op["diagnostics"]
                    record["body"] = json.dumps(body_data)

                context = {}
                result = lambda_handler(message_body, context)

                self.assertIn("200", str(result["statusCode"]))

                self.assertEqual(len(log.output), 3)

                for record_log in log.output[:2]:
                    log_json = self.extract_log_json(record_log)
                    self.assertEqual(log_json["operation_requested"], op["operation_request"])
                    self.assertEqual(log_json["diagnostics"], op["diagnostics"].get("error_message"))

                self.assertEqual(mock_send_log_to_firehose.call_count, 3)
                mock_send_log_to_firehose.reset_mock()


if __name__ == "__main__":
    unittest.main()
