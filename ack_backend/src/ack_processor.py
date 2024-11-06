import json
import os
from boto3 import client as boto3_client
from update_ack_file import update_ack_file


sqs_client = boto3_client("sqs", region_name="eu-west-2")


def lambda_handler(event, context):
    queue_url = os.environ["SQS_QUEUE_URL"]

    try:
        # Receive message from SQS queue
        response = sqs_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=20, WaitTimeSeconds=0
        )

        # Check if there are any messages to process
        if "Messages" in response:
            for message in response["Messages"]:
                # Process the message
                print(f"Message: {message['Body']}")
                file_key = ""
                row_id = ""
                imms_id = ""
                update_ack_file(
                    file_key,
                    row_id,
                    successful_api_response=True,
                    diagnostics=None,
                    imms_id=imms_id,
                )
                # Delete the message from the queue
                sqs_client.delete_message(
                    QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
                )
        else:
            print("No messages to process.")

    except Exception as e:
        print(f"Error processing SQS message: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
