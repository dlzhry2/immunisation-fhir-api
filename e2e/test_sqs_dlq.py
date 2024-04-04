import unittest
import json
import boto3
import os
from utils.delete_sqs_messages import read_and_delete_messages
from botocore.exceptions import ClientError  # Handle potential errors


class TestSQS(unittest.TestCase):
    def setUp(self):
        # Replace with your SQS queue URL
        self.queue_url = os.environ["DLQ_ARN"]
        read_and_delete_messages(self.queue_url)
        
    def test_send_message(self):
        # Create a message
        message_body = {"message": "This is a test message"}
        # Use boto3 to interact with SQS
        sqs_client = boto3.client("sqs")
        try:
            # Send the message to the queue
            response = sqs_client.send_message(
                QueueUrl=self.queue_url, MessageBody=json.dumps(message_body)
            )
            # Assert successful message sending
            self.assertIn("MessageId", response)
        except ClientError as e:
            self.fail(f"Error sending message to SQS: {e}")


if __name__ == "__main__":
    unittest.main()
