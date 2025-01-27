"""Ack lambda handler"""

import json
from typing import Union
from logging_decorators import (
    ack_lambda_handler_logging_decorator,
    convert_messsage_to_ack_row_logging_decorator,
)
from update_ack_file import update_ack_file, create_ack_data


def get_error_message_for_ack_file(message_diagnostics) -> Union[None, str]:
    """Determines and returns the error message to be displayed in the ack file"""
    if message_diagnostics is None:
        return None

    if not isinstance(message_diagnostics, dict):
        return "Unable to determine diagnostics issue"

    if message_diagnostics.get("statusCode") in (None, 500):
        return "An unhandled error occurred during batch processing"

    return message_diagnostics.get(
        "error_message", "Unable to determine diagnostics issue"
    )


@convert_messsage_to_ack_row_logging_decorator
def convert_message_to_ack_row(message, created_at_formatted_string):
    """
    Takes a single message and returns the ack data row for that message.
    A value error is raised if the file_key or created_at_formatted_string for the message do not match the
    expected values.
    """
    diagnostics = message.get("diagnostics")
    return create_ack_data(
        created_at_formatted_string=created_at_formatted_string,
        local_id=message.get("local_id"),
        row_id=message.get("row_id"),
        successful_api_response=diagnostics
        is None,  # Response is successful if and only if there are no diagnostics
        diagnostics=get_error_message_for_ack_file(diagnostics),
        imms_id=message.get("imms_id"),
    )


@ack_lambda_handler_logging_decorator
def lambda_handler(event, context):
    """
    Ack lambda handler.
    For each record: each message in the array of messages is converted to an ack row,
    then all of the ack rows for that array of messages are uploaded to the ack file in one go.
    """

    if not event.get("Records"):
        raise ValueError(
            "Error in ack_processor_lambda_handler: No records found in the event"
        )

    file_key = None
    created_at_formatted_string = None

    ack_data_rows = []

    for i, record in enumerate(event["Records"]):

        try:
            incoming_message_body = json.loads(record["body"])
        except Exception as body_json_error:
            raise ValueError(
                "Could not load incoming message body"
            ) from body_json_error

        if i == 0:
            # IMPORTANT NOTE: An assumption is made here that the file_key and created_at_formatted_string are the same
            # for all messages in the event. The use of FIFO SQS queues ensures that this is the case.
            file_key = incoming_message_body[0].get("file_key")
            message_id = (incoming_message_body[0].get("row_id")).split("^")[0]
            vaccine_type = incoming_message_body[0].get("vaccine_type")
            supplier = incoming_message_body[0].get("supplier")
            supplier_queue = f"{supplier}_{vaccine_type}"
            created_at_formatted_string = incoming_message_body[0].get(
                "created_at_formatted_string"
            )

        for message in incoming_message_body:
            ack_data_rows.append(
                convert_message_to_ack_row(message, created_at_formatted_string)
            )

    update_ack_file(
        file_key, message_id, supplier_queue, created_at_formatted_string, ack_data_rows
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
