import unittest
from unittest.mock import patch
from boto3 import client as boto3_client
from moto import mock_s3
import json
from typing import Optional
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
class TestFunctionInfoDecorator(unittest.TestCase):

    event_file = {
        "Records": [{"s3": {"bucket": {"name": SOURCE_BUCKET_NAME}, "object": {"key": VALID_FLU_EMIS_FILE_KEY}}}]
    }

    def test_splunk_logger_successful_validation(self):
        """Tests the splunk logger is called when file validation is successful"""
        set_up_s3_buckets_and_upload_file()
        config_content = {"all_permissions": {"EMIS": ["FLU_FULL"]}}

        with (  # noqa: E999
            patch(  # noqa: E999
                "initial_file_validation.get_supplier_permissions",  # noqa: E999
                return_value=["FLU_CREATE", "FLU_UPDATE"],  # noqa: E999
            ),  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue"),  # noqa: E999
            patch("file_name_processor.add_to_audit_table", return_value=True),  # noqa: E999
            patch("fetch_permissions.redis_client.get", return_value=json.dumps(PERMISSION_JSON)),  # noqa: E999
            patch(  # noqa: E999
                "initial_file_validation.get_permissions_config_json_from_cache",  # noqa: E999
                return_value=config_content,  # noqa: E999
            ),  # noqa: E999
            patch("log_structure.send_log_to_firehose") as mock_send_log_to_firehose,  # noqa: E999
            patch("log_structure.logger") as mock_logger,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.event_file, context=None)

        log_call_args = mock_logger.info.call_args[0][0]
        log_data = json.loads(log_call_args)

        self.assertTrue(mock_logger.info.called)
        self.assertTrue(mock_send_log_to_firehose.called)
        log_data = json.loads(log_call_args)

        self.assertEqual(log_data["function_name"], "handle_record")
        self.assertEqual(log_data["statusCode"], 200)

        mock_send_log_to_firehose.assert_called_with(log_data)

    def test_splunk_logger_failed_validation(self):
        """Tests the splunk logger is called when file validation is unsuccessful"""
        set_up_s3_buckets_and_upload_file(file_content=VALID_FILE_CONTENT)

        with (  # noqa: E999
            patch("file_name_processor.add_to_audit_table", return_value=True),  # noqa: E999
            patch("initial_file_validation.get_supplier_permissions", return_value=["COVID19_CREATE"]),  # noqa: E999
            patch("fetch_permissions.redis_client.get", return_value=json.dumps(PERMISSION_JSON)),  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue") as mock_send_to_supplier_queue,  # noqa: E999
            patch("log_structure.send_log_to_firehose") as mock_send_log_to_firehose,  # noqa: E999
            patch("log_structure.logger") as mock_logger,  # noqa: E999
            patch("initial_file_validation.get_permissions_config_json_from_cache"),  # noqa: E999
        ):
            lambda_handler(self.event_file, context=None)

        mock_send_to_supplier_queue.assert_not_called()
        # TODO: Fix the below assertion - need to ascertain what the status should be in this case
        # self.assertEqual(result["statusCode"], 400)
        # self.assertIn("Infrastructure Level Response Value - Processing Error", result["body"])
        # filename = result["file_info"][0]["filename"]
        # self.assertEqual(filename, VALID_FLU_EMIS_FILE_KEY)
        # self.assertIn("message_id", result["file_info"][0])
        log_call_args = mock_logger.info.call_args[0][0]
        log_data = json.loads(log_call_args)

        self.assertTrue(mock_logger.info.called)
        self.assertTrue(mock_send_log_to_firehose.called)
        log_data = json.loads(log_call_args)

        self.assertEqual(log_data["function_name"], "handle_record")
        # TODO: Fix the below assertion - need to ascertain what the status should be in this case
        # self.assertEqual(log_data["status"], 400)

        # # Assert - Check Firehose log call
        mock_send_log_to_firehose.assert_called_with(log_data)
