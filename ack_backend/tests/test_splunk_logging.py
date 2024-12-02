import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from src.ack_processor import lambda_handler
from update_ack_file import update_ack_file
from log_firehose_splunk import FirehoseLogger
from log_structure_splunk import logger


class TestSplunkFunctionInfo(unittest.TestCase):

    def setUp(self):
        self.message_body_base = {
            "Records": [
                {
                    "body": json.dumps(
                        [
                            {
                                "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
                                "row_id": "123",
                                "local_id": "local_123",
                                "action_flag": "action_flag",
                                "imms_id": "1232",
                                "created_at_formatted_string": "1223-12-232",
                                "supplier": "DPSFULL",
                            }
                        ]
                    )
                }
            ]
        }

        self.fixed_datetime = datetime(2024, 10, 29, 12, 0, 0)

        self.test_fixed_time_taken = [
            1000000.0,
            1000001.0,
            1000001.0,
            1000000.0,
            1000001.0,
            1000001.0,
            1000000.0,
            1000001.0,
            1000001.0,
        ]

        self.message_body_two_base = {
            "Records": [
                {
                    "body": json.dumps(
                        [
                            {
                                "file_key": "RSV_Vaccinations_v5_YGM41_20240905T13005922",
                                "row_id": "456",
                                "local_id": "local_456",
                                "action_flag": "action_flag",
                                "imms_id": "4567",
                                "created_at_formatted_string": "1223-12-232",
                                "supplier": "EMIS",
                            },
                            {
                                "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
                                "row_id": "123",
                                "local_id": "local_123",
                                "action_flag": "action_flag",
                                "imms_id": "1232",
                                "created_at_formatted_string": "1223-12-232",
                                "supplier": "DPSFULL",
                            },
                        ]
                    )
                }
            ]
        }

        self.expected_values = {
            "function_name": "lambda_handler",
            "date_time": self.fixed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success",
            "supplier": "DPSFULL",
            "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
            "vaccine_type": "RSV",
            "message_id": "123",
            "operation_requested": "action_flag",
            "time_taken": "1.0s",
        }

    def extract_log_json(self, log_entry):
        """Extracts JSON from log entry."""
        json_start = log_entry.find("{")
        json_str = log_entry[json_start:]
        return json.loads(json_str)

    @patch("ack_processor.create_ack_data")
    @patch("ack_processor.update_ack_file")
    @patch("log_structure_splunk.firehose_logger")
    @patch("time.time")
    @patch("log_structure_splunk.datetime")
    def test_splunk_logging_successful_rows(
        self, mock_datetime, mock_time, mock_firehose_logger, mock_create_ack_data, mock_update_ack_file
    ):

        # mocking datetime and time_taken as fixed values
        mock_datetime.now.return_value = self.fixed_datetime
        mock_time.side_effect = self.test_fixed_time_taken

        mock_create_ack_data.return_value = None
        mock_update_ack_file.return_value = {}
        operations = [
            {"operation_request": "CREATE"},
            {"operation_request": "UPDATE"},
            {"operation_request": "DELETE"},
        ]

        for op in operations:
            with self.assertLogs(level="INFO") as log:
                message_body = self.message_body_base.copy()

                # Iterate over each record in the message body and update action_flag
                for record in message_body["Records"]:
                    body_data = json.loads(record["body"])
                    for item in body_data:
                        item["action_flag"] = op["operation_request"]  # Assign the operation to action_flag
                    record["body"] = json.dumps(body_data)

                context = {}

                result = lambda_handler(message_body, context)
                self.assertIn("200", str(result["statusCode"]))
                self.assertGreater(len(log.output), 0)

                log_json = self.extract_log_json(log.output[0])

                expected_values = self.expected_values
                expected_values["operation_requested"] = op["operation_request"]

                # Iterate over the expected values and assert each one
                for key, expected in expected_values.items():
                    self.assertEqual(log_json[key], expected)

                self.assertIsInstance(log_json["time_taken"], str)

                # Check firehose logging call
                mock_firehose_logger.ack_send_log.assert_called_once_with({"event": log_json})
                mock_firehose_logger.ack_send_log.reset_mock()

    @patch("ack_processor.create_ack_data")
    @patch("ack_processor.update_ack_file")
    @patch("log_structure_splunk.firehose_logger")
    @patch("time.time")
    @patch("log_structure_splunk.datetime")
    def test_splunk_logging_multiple_rows(
        self, mock_datetime, mock_time, mock_firehose_logger, mock_create_ack_data, mock_update_ack_file
    ):

        # mocking datetime and time_taken as fixed values
        mock_datetime.now.return_value = self.fixed_datetime
        mock_time.side_effect = self.test_fixed_time_taken

        mock_create_ack_data.return_value = None
        mock_update_ack_file.return_value = {}
        operations = [
            {"operation_request": "CREATE"},
            {"operation_request": "UPDATE"},
            {"operation_request": "DELETE"},
        ]

        for op in operations:
            with self.assertLogs(level="INFO") as log:
                message_body = self.message_body_two_base.copy()

                # Iterate over each record in the message body and update action_flag
                for record in message_body["Records"]:
                    body_data = json.loads(record["body"])
                    for item in body_data:
                        item["action_flag"] = op["operation_request"]
                    record["body"] = json.dumps(body_data)

                context = {}

                result = lambda_handler(message_body, context)
                self.assertIn("200", str(result["statusCode"]))
                self.assertGreater(len(log.output), 0)

                log_json = self.extract_log_json(log.output[0])

                expected_values = self.expected_values
                expected_values["operation_requested"] = op["operation_request"]

                # Iterate over the expected values and assert each one
                for key, expected in expected_values.items():
                    self.assertEqual(log_json[key], expected)

                self.assertIsInstance(log_json["time_taken"], str)

                # Check firehose logging call
                mock_firehose_logger.ack_send_log.assert_called_once_with({"event": log_json})
                mock_firehose_logger.ack_send_log.reset_mock()

    @patch("ack_processor.create_ack_data")
    @patch("ack_processor.update_ack_file")
    @patch("log_structure_splunk.firehose_logger")
    @patch("time.time")
    @patch("log_structure_splunk.datetime")
    def test_splunk_logging_multiple_with_diagnostics(
        self, mock_datetime, mock_time, mock_firehose_logger, mock_create_ack_data, mock_update_ack_file
    ):

        # mocking datetime and time_taken as fixed values
        mock_datetime.now.return_value = self.fixed_datetime
        mock_time.side_effect = self.test_fixed_time_taken

        mock_create_ack_data.return_value = None
        mock_update_ack_file.return_value = {}
        operations = [
            {"operation_request": "CREATE", "diagnostics": "some_create_diagnostic"},
            {"operation_request": "UPDATE", "diagnostics": "some_update_diagnostic"},
            {"operation_request": "DELETE", "diagnostics": "some_delete_diagnostic"},
        ]

        for op in operations:
            with self.assertLogs(level="INFO") as log:
                message_body = self.message_body_two_base.copy()

                for record in message_body["Records"]:
                    body_data = json.loads(record["body"])
                    for item in body_data:
                        item["action_flag"] = op["operation_request"]
                        item["diagnostics"] = op["diagnostics"]
                    record["body"] = json.dumps(body_data)

                context = {}

                # print(f"MESSAGEEETTT: {message_body}")

                context = {}

                result = lambda_handler(message_body, context)
                self.assertIn("200", str(result["statusCode"]))
                # print(f"RESLT: {result}")
                self.assertGreater(len(log.output), 0)

                log_json = self.extract_log_json(log.output[0])
                # print(log_json)

                expected_values = self.expected_values.copy()
                expected_values["operation_requested"] = op["operation_request"]
                expected_values["status"] = "fail"
                expected_values["diagnostics"] = op["diagnostics"]

                # Iterate over the expected values and assert each one
                for key, expected in expected_values.items():
                    self.assertEqual(log_json[key], expected)

                self.assertIsInstance(log_json["time_taken"], str)

                # Check firehose logging call
                mock_firehose_logger.ack_send_log.assert_called_once_with({"event": log_json})
                mock_firehose_logger.ack_send_log.reset_mock()


if __name__ == "__main__":
    unittest.main()
