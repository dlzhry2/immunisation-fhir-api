"""Functions to send a message to SQS"""

import logging
import os
from json import dumps as json_dumps
from utils_for_filenameprocessor import extract_file_key_elements
from clients import sqs_client


logger = logging.getLogger()


def send_to_supplier_queue(message_body: dict) -> bool:
    """Sends a message to the supplier queue and returns a bool indicating if the message has been successfully sent"""
    try:
        supplier = message_body["supplier"]
        queue_url = os.getenv("QUEUE_URL")
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json_dumps(message_body), MessageGroupId=supplier)
        logger.info("Message sent to SQS queue for supplier: %s", supplier)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.error("An unexpected error occurred whilst sending to SQS: %s", error)
        return False
    return True


def make_message_body_for_sqs(
    file_key: str, message_id: str, permission: str, created_at_formatted_string: str
) -> dict:
    """Returns the message body for the message which will be sent to SQS"""
    file_key_elements = extract_file_key_elements(file_key)
    return {
        "message_id": message_id,
        "vaccine_type": file_key_elements["vaccine_type"],
        "supplier": file_key_elements["supplier"],
        "timestamp": file_key_elements["timestamp"],
        "filename": file_key,
        "permission": permission,
        "created_at_formatted_string": created_at_formatted_string,
    }


def make_and_send_sqs_message(
    file_key: str, message_id: str, permission: str, created_at_formatted_string: str
) -> bool:
    """
    Attempts to send a message to the SQS queue.
    Returns a bool to indication if the message has been sent successfully.
    """
    message_body = make_message_body_for_sqs(
        file_key=file_key,
        message_id=message_id,
        permission=permission,
        created_at_formatted_string=created_at_formatted_string,
    )
    return send_to_supplier_queue(message_body)
