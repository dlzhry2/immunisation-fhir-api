# """Tests for Splunk logging"""

import unittest
from unittest.mock import patch
import json
from datetime import datetime
from src.ack_processor import lambda_handler

from update_ack_file import update_ack_file, obtain_current_ack_content, upload_ack_file


class TestSplunkFunctionInfo(unittest.TestCase):

    @patch("ack_processor.update_ack_file")
    @patch("update_ack_file.obtain_current_ack_content")
    @patch("update_ack_file.upload_ack_file")
    @patch("log_structure_splunk.logger")
    @patch("log_structure_splunk.firehose_logger")
    def test_lambda_handler_success(
        self,
        mock_firehose_logger,
        mock_logger,
        mock_update_ack_file,
        mock_obtain_current_ack_content,
        mock_upload_ack_file,
    ):
        """Test that lambda_handler logs successfully when no errors occur"""

        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
                            "row_id": "123",
                            "local_id": "local_123",
                            "operation_requested": "create",
                            "imms_id": "1232",
                            "created_at_formatted_string": "1223-12-232",
                        }
                    )
                }
            ]
        }

        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response["statusCode"], 200)

        log_call = mock_logger.info.call_args_list[0][0]
        # print(f"logger call arguments: {mock_logger.info.call_args_list}")
        log_data = json.loads(log_call[0])
        # print(f"LOGCA000000: {log_call}")

        self.assertEqual(log_data["status"], "success")
        self.assertEqual(log_data["statusCode"], 200)
        self.assertEqual(log_data["file_key"], "RSV_Vaccinations_v5_DPSFULL_20240905T13005922")
        self.assertEqual(log_data["row_id"], "123")
        self.assertEqual(log_data["local_id"], "local_123")
        self.assertEqual(log_data["operation_requested"], "create")
        self.assertIn("time_taken", log_data)

        mock_obtain_current_ack_content.assert_called_once()
        # mock_update_ack_file.assert_called_once()
        mock_upload_ack_file.assert_called_once()
        mock_firehose_logger.ack_send_log.assert_called_once()

    @patch("ack_processor.update_ack_file")
    @patch("update_ack_file.obtain_current_ack_content")
    @patch("update_ack_file.upload_ack_file")
    @patch("log_structure_splunk.logger")
    @patch("log_structure_splunk.firehose_logger")
    def test_lambda_handler_failure(
        self,
        mock_firehose_logger,
        mock_logger,
        mock_update_ack_file,
        mock_obtain_current_ack_content,
        mock_upload_ack_file,
    ):
        """Test that lambda_handler logs a failure when an exception occurs"""

        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
                            "row_id": "123",
                            "local_id": "local_123",
                            "diagnostics": "something wrong",
                            "imms_id": "1232",
                            "created_at_formatted_string": "1223-12-232",
                        }
                    )
                }
            ]
        }

        context = {}

        lambda_handler(event, context)

        log_call = mock_logger.info.call_args_list[0][0]
        # print(f"logger call arguments: {mock_logger.exception.call_args_list}")
        log_data = json.loads(log_call[0])
        print(f"LOGCA1111: {log_call}")

        self.assertEqual(log_data["status"], "fail")
        self.assertEqual(log_data["statusCode"], 400)
        self.assertIn("diagnostics", log_data)
        # self.assertIn("error_source", log_data)
        # self.assertEqual(log_data["error_source"], "lambda_handler")
        self.assertIn("time_taken", log_data)

        mock_obtain_current_ack_content.assert_called_once()
        # mock_update_ack_file.assert_called_once()
        mock_upload_ack_file.assert_called_once()
        mock_firehose_logger.ack_send_log.assert_called_once()

    @patch("ack_processor.update_ack_file")
    @patch("update_ack_file.obtain_current_ack_content")
    @patch("update_ack_file.upload_ack_file")
    @patch("log_structure_splunk.logger")
    @patch("log_structure_splunk.firehose_logger")
    def test_lambda_handler_error(
        self,
        mock_firehose_logger,
        mock_logger,
        mock_update_ack_file,
        mock_obtain_current_ack_content,
        mock_upload_ack_file,
    ):
        """Test that lambda_handler logs a failure when an exception occurs"""
        event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "file_key": "RSV_Vaccinations_v5_DPSFULL_20240905T13005922",
                            "row_id": "123",
                            "local_id": "local_123",
                            "diagnostics": "internal server error",
                        }
                    )
                }
            ]
        }

        context = {}

        lambda_handler(event, context)

        log_call = mock_logger.info.call_args_list[0][0]
        # print(f"logger call arguments: {mock_logger.exception.call_args_list}")
        log_data = json.loads(log_call[0])
        print(f"LOGCA1111: {log_call}")

        self.assertEqual(log_data["status"], "fail")
        self.assertEqual(log_data["statusCode"], 500)
        self.assertIn("diagnostics", log_data)
        # self.assertIn("error_source", log_data)
        # self.assertEqual(log_data["error_source"], "lambda_handler")
        self.assertIn("time_taken", log_data)

        mock_obtain_current_ack_content.assert_called_once()
        # mock_update_ack_file.assert_called_once()
        mock_upload_ack_file.assert_called_once()
        mock_firehose_logger.ack_send_log.assert_called_once()


if __name__ == "__main__":
    unittest.main()
