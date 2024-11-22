"""Functions for forwarding each row to the Imms API"""

import os
import simplejson as json
import base64
import logging
from models.errors import MessageNotSuccessfulError
from fhir_batch_repository import create_table
from fhir_batch_controller import ImmunizationBatchController, make_batch_controller
from clients import sqs_client

logging.basicConfig(level="INFO")
logger = logging.getLogger()

QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def forward_request_to_dynamo(message_body: any, table: any, batchcontroller: ImmunizationBatchController):
    """Forwards the request to the Imms API (where possible) and updates the ack file with the outcome"""
    row_id = message_body.get("row_id")
    try:
        return batchcontroller.send_request_to_dynamo(message_body, table)
    except MessageNotSuccessfulError as error:
        logger.info("Error: %s", error)
    logger.info("FORWARDED MESSAGE: ID %s", row_id)


def forward_lambda_handler(event, _):
    """Forward each row to the Imms API"""
    logger.info("Processing started")
    table = create_table()
    controller = make_batch_controller()
    for record in event["Records"]:
        try:
            kinesis_payload = record["kinesis"]["data"]
            decoded_payload = base64.b64decode(kinesis_payload).decode("utf-8")
            message_body = json.loads(decoded_payload, use_decimal=True)
            file_key = message_body.get("file_key")
            row_id = message_body.get("row_id")
            response = forward_request_to_dynamo(message_body, table, controller)
            response["file_key"] = file_key
            response["row_id"] = row_id           
            sqs_client.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(response), MessageGroupId=file_key)
        except Exception as error:  # pylint:disable=broad-exception-caught
            logger.error("Error processing message: %s", error)
    logger.info("Processing ended")


if __name__ == "__main__":
    forward_lambda_handler({"Records": []}, {})
