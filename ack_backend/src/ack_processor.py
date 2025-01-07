"""Ack lambda handler"""

import json
from logging_decorators import ack_lambda_handler_logging_decorator, convert_messsage_to_ack_row_logging_decorator
from update_ack_file import update_ack_file, create_ack_data


@convert_messsage_to_ack_row_logging_decorator
def convert_message_to_ack_row(message, expected_file_key, expected_created_at_formatted_string):
    """
    Takes a single message and returns the ack data row for that message.
    A value error is raised if the file_key or created_at_formatted_string for the message do not match the
    expected values.
    """
    # Check that the file_key and created_at_formatted_string are the same for each message
    if message.get("file_key") != expected_file_key:
        raise ValueError("File key mismatch")
    if message.get("created_at_formatted_string") != expected_created_at_formatted_string:
        raise ValueError("Created_at_formatted_string mismatch")

    if (diagnostics := message.get("diagnostics")) is not None and not isinstance(diagnostics, dict):
        raise ValueError("Diagnostics must be either None or a dictionary")

    return create_ack_data(
        created_at_formatted_string=expected_created_at_formatted_string,
        local_id=message.get("local_id"),
        row_id=message.get("row_id"),
        successful_api_response=diagnostics is None,  # Response is successful if and only if there are no diagnostics
        diagnostics=diagnostics.get("error_message") if diagnostics else None,
        imms_id=message.get("imms_id"),
    )


@ack_lambda_handler_logging_decorator
def lambda_handler(event, context):

    if not event.get("Records"):
        raise ValueError("Error in ack_processor_lambda_handler: No records found in the event")

    for record in event["Records"]:

        try:
            incoming_message_body = json.loads(record["body"])
        except Exception as body_json_error:
            raise ValueError("Could not load incoming message body") from body_json_error

        # file_key and created_at_formatted_string should be the same for all messages in the incoming_message_body
        file_key = incoming_message_body[0].get("file_key")
        created_at_formatted_string = incoming_message_body[0].get("created_at_formatted_string")
        array_of_rows = []

        for message in incoming_message_body:
            array_of_rows.append(convert_message_to_ack_row(message, file_key, created_at_formatted_string))

        update_ack_file(file_key, created_at_formatted_string=created_at_formatted_string, ack_data_rows=array_of_rows)

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
