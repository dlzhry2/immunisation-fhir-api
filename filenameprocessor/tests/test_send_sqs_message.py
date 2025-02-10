"""Tests for send_sqs_message functions"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from json import loads as json_loads
from copy import deepcopy
from moto import mock_sqs
from boto3 import client as boto3_client

from tests.utils_for_tests.values_for_tests import MOCK_ENVIRONMENT_DICT, MockFileDetails, Sqs

# Ensure environment variables are mocked before importing from src files
with patch.dict("os.environ", MOCK_ENVIRONMENT_DICT):
    from send_sqs_message import send_to_supplier_queue, make_and_send_sqs_message
    from errors import UnhandledSqsError, InvalidSupplierError
    from clients import REGION_NAME

sqs_client = boto3_client("sqs", region_name=REGION_NAME)

FILE_DETAILS = MockFileDetails.flu_emis

NON_EXISTENT_QUEUE_ERROR_MESSAGE = (
    "An unexpected error occurred whilst sending to SQS: An error occurred (AWS.SimpleQueueService.NonExistent"
    + "Queue) when calling the SendMessage operation: The specified queue does not exist for this wsdl version."
)


@mock_sqs
@patch.dict("os.environ", MOCK_ENVIRONMENT_DICT)
class TestSendSQSMessage(TestCase):
    """Tests for send_sqs_message functions"""

    def test_send_to_supplier_queue_success(self):
        """Test send_to_supplier_queue function for a successful message send"""
        # Set up the sqs_queue
        queue_url = sqs_client.create_queue(QueueName=Sqs.QUEUE_NAME, Attributes=Sqs.ATTRIBUTES)["QueueUrl"]

        self.assertIsNone(
            send_to_supplier_queue(
                message_body=deepcopy(FILE_DETAILS.sqs_message_body),
                vaccine_type=FILE_DETAILS.vaccine_type,
                supplier=FILE_DETAILS.supplier,
            )
        )

        # Assert that correct message has reached the queue
        messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        self.assertEqual(json_loads(messages["Messages"][0]["Body"]), FILE_DETAILS.sqs_message_body)

    def test_send_to_supplier_queue_failure_due_to_queue_does_not_exist(self):
        """Test send_to_supplier_queue function for a failed message send due to queue not existing"""
        with self.assertRaises(UnhandledSqsError) as context:
            send_to_supplier_queue(
                message_body=deepcopy(FILE_DETAILS.sqs_message_body),
                vaccine_type=FILE_DETAILS.vaccine_type,
                supplier=FILE_DETAILS.supplier,
            )
        self.assertEqual(NON_EXISTENT_QUEUE_ERROR_MESSAGE, str(context.exception))

    def test_send_to_supplier_queue_failure_due_to_absent_supplier_or_vaccine_type(self):
        """Test send_to_supplier_queue function for a failed message send"""
        # Set up the sqs_queue
        sqs_client.create_queue(QueueName=Sqs.QUEUE_NAME, Attributes=Sqs.ATTRIBUTES)
        expected_error_message = (
            "Message not sent to supplier queue as unable to identify supplier and/ or vaccine type"
        )

        keys_to_set_to_empty = ["supplier", "vaccine_type"]
        for key_to_set_to_empty in keys_to_set_to_empty:
            with self.subTest(f"{key_to_set_to_empty} set to empty string"):
                mock_sqs_client = MagicMock()
                with patch("send_sqs_message.sqs_client", mock_sqs_client):
                    with self.assertRaises(InvalidSupplierError) as context:
                        message_body = {**FILE_DETAILS.sqs_message_body, key_to_set_to_empty: ""}
                        vaccine_type = message_body["vaccine_type"]
                        supplier = message_body["supplier"]
                        send_to_supplier_queue(message_body, supplier, vaccine_type)
                self.assertEqual(str(context.exception), expected_error_message)
                mock_sqs_client.send_message.assert_not_called()

    def test_make_and_send_sqs_message_success(self):
        """Test make_and_send_sqs_message function for a successful message send"""
        # Create a mock SQS queue
        queue_url = sqs_client.create_queue(QueueName=Sqs.QUEUE_NAME, Attributes=Sqs.ATTRIBUTES)["QueueUrl"]

        # Call the send_to_supplier_queue function
        self.assertIsNone(
            make_and_send_sqs_message(
                file_key=FILE_DETAILS.file_key,
                message_id=FILE_DETAILS.message_id,
                permission=deepcopy(FILE_DETAILS.permissions_list),
                vaccine_type=FILE_DETAILS.vaccine_type,
                supplier=FILE_DETAILS.supplier,
                created_at_formatted_string=FILE_DETAILS.created_at_formatted_string,
            )
        )

        # Assert that correct message has reached the queue
        messages = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        self.assertEqual(json_loads(messages["Messages"][0]["Body"]), deepcopy(FILE_DETAILS.sqs_message_body))

    def test_make_and_send_sqs_message_failure(self):
        """Test make_and_send_sqs_message function for a failure due to queue not existing"""
        with self.assertRaises(UnhandledSqsError) as context:
            make_and_send_sqs_message(
                file_key=FILE_DETAILS.file_key,
                message_id=FILE_DETAILS.message_id,
                permission=deepcopy(FILE_DETAILS.permissions_list),
                vaccine_type=FILE_DETAILS.vaccine_type,
                supplier=FILE_DETAILS.supplier,
                created_at_formatted_string=FILE_DETAILS.created_at_formatted_string,
            )
        self.assertIn(NON_EXISTENT_QUEUE_ERROR_MESSAGE, str(context.exception))
