"""Tests for lambda_handler"""

from unittest.mock import patch
from unittest import TestCase
from io import BytesIO
from json import loads as json_loads, dumps as json_dumps
from typing import Optional
from copy import deepcopy
from boto3 import client as boto3_client
from moto import mock_s3, mock_sqs, mock_firehose, mock_dynamodb
from clients import REGION_NAME
from file_name_processor import lambda_handler
from tests.utils_for_tests.utils_for_filenameprocessor_tests import generate_permissions_config_content
from tests.utils_for_tests.values_for_tests import (
    MOCK_ENVIRONMENT_DICT,
    STATIC_DATETIME,
    STATIC_DATETIME_FORMATTED,
    BucketNames,
    Sqs,
    MockFileDetails,
)


s3_client = boto3_client("s3", region_name=REGION_NAME)
sqs_client = boto3_client("sqs", region_name=REGION_NAME)


@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
@patch("logging_decorator.STREAM_NAME", "immunisation-fhir-api-internal-dev-splunk-firehose")
@mock_s3
@mock_sqs
@mock_firehose
@mock_dynamodb
class TestLambdaHandler(TestCase):
    """Tests for lambda_handler. NOTE: All helper functions default to use FLU/ EMIS file details."""

    def setUp(self):
        self.mock_config_file_content = BytesIO(b"mock_file_content")
        self.mock_elasticcache_get_object_return_value = {"Body": self.mock_config_file_content}

    def tearDown(self):
        self.mock_config_file_content.close()

    def set_up_s3_buckets_and_upload_file(self, file_key: Optional[str] = None, file_content: str = None):
        """
        Sets up the source and destination buckets and uploads the test file to the source bucket.
        Returns the S3 client.
        """
        for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION]:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION_NAME})

        s3_client.put_object(
            Bucket=BucketNames.SOURCE,
            Key=file_key or MockFileDetails.flu_emis.file_key,
            Body=file_content or "mock_file_content",
        )

    @staticmethod
    def make_event(file_key: Optional[str] = None):
        """
        Makes an event with s3 bucket name set to BucketNames.SOURCE and
        and s3 object key set to the file_key if given, else the MockFileDetails.flu_emis.file_key
        """
        s3 = {
            "bucket": {"name": BucketNames.SOURCE},
            "object": {"key": (file_key or MockFileDetails.flu_emis.file_key)},
        }
        return {"Records": [{"s3": s3}]}

    config_event = {
        "Records": [
            {"s3": {"bucket": {"name": BucketNames.CONFIG}, "object": {"key": (MockFileDetails.flu_emis.file_key)}}}
        ]
    }

    @staticmethod
    def get_ack_file_key(file_key: str) -> str:
        """Returns the ack file key for the given file key"""
        response = s3_client.get_object(Bucket=BucketNames.SOURCE, Key=file_key)
        created_at_formatted_string = response["LastModified"].strftime("%Y%m%dT%H%M%S00")
        return f"ack/{file_key.replace('.csv', '_InfAck_' + created_at_formatted_string + '.csv')}"

    def assert_ack_file_in_destination_s3_bucket(self, ack_file_key: Optional[str] = None):
        """Assert that the ack file if given, else the VALID_FLU_EMIS_ACK_FILE_KEY, is in the destination S3 bucket"""
        ack_file_key = ack_file_key if ack_file_key else self.get_ack_file_key(MockFileDetails.flu_emis.file_key)
        ack_files_in_destination_bucket = s3_client.list_objects_v2(Bucket=BucketNames.DESTINATION)
        ack_file_keys_in_destination_bucket = [
            obj["Key"] for obj in ack_files_in_destination_bucket.get("Contents", [])
        ]
        self.assertIn(ack_file_key, ack_file_keys_in_destination_bucket)

    def test_add_to_audit_table_called(self):
        """Tests that add_to_audit_table is called with the correct input args"""
        self.set_up_s3_buckets_and_upload_file()
        mock_last_modified = {"LastModified": STATIC_DATETIME}

        with (  # noqa: E999
            patch("file_name_processor.uuid4", return_value="test_id"),  # noqa: E999
            patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
            patch("file_name_processor.s3_client.get_object", return_value=mock_last_modified),  # noqa: E999
            patch("file_name_processor.add_to_audit_table") as mock_add_to_audit_table,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.make_event(), None)

        mock_add_to_audit_table.assert_called_with(
            "test_id", MockFileDetails.flu_emis.file_key, STATIC_DATETIME_FORMATTED
        )

    def test_lambda_invalid_file_key(self):
        """tests SQS queue is not called when file key includes invalid file key"""
        test_file_key = "InvalidVaccineType_Vaccinations_v5_YGM41_20240708T12130100.csv"
        self.set_up_s3_buckets_and_upload_file(file_key=test_file_key)

        permissions_config_content = json_dumps({"all_permissions": {"EMIS": ["FLU_FULL"]}})

        with (  # noqa: E999
            patch("supplier_permissions.redis_client.get", return_value=permissions_config_content),  # noqa: E999
            patch("file_name_processor.add_to_audit_table"),  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue") as mock_send_to_supplier_queue,  # noqa: E999
            patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
        ):  # noqa: E999
            lambda_handler(event=self.make_event(test_file_key), context=None)

        mock_send_to_supplier_queue.assert_not_called()
        self.assert_ack_file_in_destination_s3_bucket(ack_file_key=self.get_ack_file_key(test_file_key))

    def test_lambda_invalid_permissions(self):
        """Tests that SQS queue is not called when supplier has no permissions for the vaccine type"""
        self.set_up_s3_buckets_and_upload_file()

        # Mock the supplier permissions with a value which doesn't include the requested Flu permissions
        permissions_config_content = json_dumps({"all_permissions": {"EMIS": ["RSV_DELETE"]}})

        # and send_to_supplier_queue functions
        with (  # noqa: E999
            patch("send_sqs_message.send_to_supplier_queue") as mock_send_to_supplier_queue,  # noqa: E999
            patch("file_name_processor.add_to_audit_table"),  # noqa: E999
            patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
            patch("supplier_permissions.redis_client.get", return_value=permissions_config_content),  # noqa: E999
        ):  # noqa: E999
            lambda_handler(event=self.make_event(MockFileDetails.flu_emis.file_key), context=None)

        mock_send_to_supplier_queue.assert_not_called()
        self.assert_ack_file_in_destination_s3_bucket()

    def test_lambda_handler_success(self):
        """Tests that lambda handler runs successfully for files with valid file keys and permissions."""
        # Set up S3 and SQS
        for bucket_name in [BucketNames.SOURCE, BucketNames.DESTINATION]:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION_NAME})
        queue_url = sqs_client.create_queue(QueueName=Sqs.QUEUE_NAME, Attributes=Sqs.ATTRIBUTES)["QueueUrl"]

        # NOTE: Add a test case for each vaccine type
        test_cases = [MockFileDetails.rsv_ravs, MockFileDetails.flu_emis]
        for file_details in test_cases:
            with self.subTest(file_details.name):
                s3_client.put_object(Bucket=BucketNames.SOURCE, Key=file_details.file_key, Body="mock_file_content")
                permissions_config_content = generate_permissions_config_content(
                    deepcopy(file_details.permissions_config)
                )
                with (  # noqa: E999
                    patch("file_name_processor.add_to_audit_table"),  # noqa: E999
                    patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
                    patch(  # noqa: E999
                        "supplier_permissions.redis_client.get", return_value=permissions_config_content  # noqa: E999
                    ),  # noqa: E999
                ):  # noqa: E999
                    lambda_handler(self.make_event(file_details.file_key), None)

                # Check if the message was sent to the SQS queue
                messages = sqs_client.receive_message(QueueUrl=queue_url, WaitTimeSeconds=1, MaxNumberOfMessages=1)
                self.assertIn("Messages", messages)
                received_message = json_loads(messages["Messages"][0]["Body"])

                # Validate message content
                self.assertEqual(received_message["vaccine_type"], file_details.vaccine_type)
                self.assertEqual(received_message["supplier"], file_details.supplier)
                self.assertEqual(received_message["filename"], file_details.file_key)
                self.assertEqual(received_message["permission"], file_details.permissions_list)

    def test_successful_processing_from_configs(self):
        mock_config_body = self.mock_elasticcache_get_object_return_value

        with (  # noqa: E999
            patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
            patch("elasticcache.redis_client.set") as mock_redis_set,  # noqa: E999
            patch(  # noqa: E999
                "elasticcache.s3_client.get_object", return_value=mock_config_body  # noqa: E999
            ) as mock_s3_get_object,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.config_event, None)

        mock_s3_get_object.assert_called_once_with(Bucket=BucketNames.CONFIG, Key=MockFileDetails.flu_emis.file_key)
        mock_redis_set.assert_called_once_with(MockFileDetails.flu_emis.file_key, "mock_file_content")

    def test_processing_from_configs_failed(self):
        elasticcache_exception = Exception("Simulated ElastiCache upload failure")
        mock_config_body = self.mock_elasticcache_get_object_return_value

        with (  # noqa: E999
            patch("logging_decorator.send_log_to_firehose"),  # noqa: E999
            patch("elasticcache.upload_to_elasticache", side_effect=elasticcache_exception),  # noqa: E999
            patch(  # noqa: E999
                "elasticcache.s3_client.get_object", return_value=mock_config_body  # noqa: E999
            ) as mock_s3_get_object,  # noqa: E999
        ):  # noqa: E999
            lambda_handler(self.config_event, None)

        mock_s3_get_object.assert_called_once_with(Bucket=BucketNames.CONFIG, Key=MockFileDetails.flu_emis.file_key)
