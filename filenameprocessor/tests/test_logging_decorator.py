"""Tests for the logging_decorator and its helper functions"""

import unittest
from unittest.mock import patch
import json
from typing import Optional
from boto3 import client as boto3_client
from moto import mock_s3
from file_name_processor import lambda_handler
from tests.utils_for_tests.values_for_tests import (
    SOURCE_BUCKET_NAME,
    PERMISSION_JSON,
    DESTINATION_BUCKET_NAME,
    VALID_FILE_CONTENT,
    MOCK_ENVIRONMENT_DICT,
    VALID_FLU_EMIS_FILE_KEY,
)


def set_up_s3_buckets_and_upload_file(file_key: Optional[str] = None, file_content: str = None):
    """
    Sets up the source and destination buckets and uploads the test file to the source bucket.
    Returns the S3 client.
    """
    s3_client = boto3_client("s3", region_name="eu-west-2")

    for bucket_name in [SOURCE_BUCKET_NAME, DESTINATION_BUCKET_NAME]:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})

    s3_client.put_object(
        Bucket=SOURCE_BUCKET_NAME, Key=file_key or VALID_FLU_EMIS_FILE_KEY, Body=file_content or VALID_FILE_CONTENT
    )

    return s3_client


@mock_s3
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestLoggingDecorator(unittest.TestCase):
    """Tests for the logging_decorator and its helper functions"""

    event_file = {
        "Records": [{"s3": {"bucket": {"name": SOURCE_BUCKET_NAME}, "object": {"key": VALID_FLU_EMIS_FILE_KEY}}}]
    }

    def test_splunk_logger_successful_validation(self):
        """Tests the splunk logger is called when file validation is successful"""
        set_up_s3_buckets_and_upload_file()

        with (  # noqa: E999
            patch("file_name_processor.uuid4", return_value="test_id"),  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue"),  # noqa: E999
            patch("file_name_processor.add_to_audit_table", return_value=True),  # noqa: E999
            patch("supplier_permissions.redis_client.get", return_value=json.dumps(PERMISSION_JSON)),  # noqa: E999
            patch("logging_decorator.send_log_to_firehose") as mock_send_log_to_firehose,  # noqa: E999
            patch("logging_decorator.logger") as mock_logger,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.event_file, context=None)

        expected_log_data = {
            "function_name": "handle_record",
            "date_time": "REPLACE THIS VALUE",
            "time_taken": "REPLACE THIS VALUE",
            "statusCode": 200,
            "message": "Successfully sent to SQS queue",
            "file_key": VALID_FLU_EMIS_FILE_KEY,
            "message_id": "test_id",
            "vaccine_type": "FLU",
            "supplier": "EMIS",
        }

        log_data = json.loads(mock_logger.info.call_args[0][0])
        expected_log_data["time_taken"] = log_data["time_taken"]
        expected_log_data["date_time"] = log_data["date_time"]
        self.assertEqual(log_data, expected_log_data)

        self.assertTrue(mock_send_log_to_firehose.called)
        mock_send_log_to_firehose.assert_called_with(log_data)

    def test_splunk_logger_failed_validation(self):
        """Tests the splunk logger is called when file validation is unsuccessful"""
        set_up_s3_buckets_and_upload_file(file_content=VALID_FILE_CONTENT)
        # Set up permissions for COVID19 only (file is for FLU), so that validation will fail
        permissions_json = {"all_permissions": {"EMIS": ["COVID19_FULL"]}}

        with (  # noqa: E999
            patch("file_name_processor.uuid4", return_value="test_id"),  # noqa: E999
            patch("file_name_processor.add_to_audit_table", return_value=True),  # noqa: E999
            patch("supplier_permissions.redis_client.get", return_value=json.dumps(permissions_json)),  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue") as mock_send_to_supplier_queue,  # noqa: E999
            patch("logging_decorator.send_log_to_firehose") as mock_send_log_to_firehose,  # noqa: E999
            patch("logging_decorator.logger") as mock_logger,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.event_file, context=None)

        mock_send_to_supplier_queue.assert_not_called()

        # TODO: Fix the below assertion - need to ascertain what the status code should be in this case
        expected_log_data = {
            "function_name": "handle_record",
            "date_time": "REPLACE THIS VALUE",
            "time_taken": "REPLACE THIS VALUE",
            "statusCode": 500,
            "message": "Infrastructure Level Response Value - Processing Error",
            "file_key": VALID_FLU_EMIS_FILE_KEY,
            "message_id": "test_id",
            "error": "Initial file validation failed: EMIS does not have permissions for FLU",
        }

        log_data = json.loads(mock_logger.info.call_args[0][0])
        expected_log_data["time_taken"] = log_data["time_taken"]
        expected_log_data["date_time"] = log_data["date_time"]
        self.assertEqual(log_data, expected_log_data)

        self.assertTrue(mock_logger.info.called)
        mock_send_log_to_firehose.assert_called_with(log_data)
