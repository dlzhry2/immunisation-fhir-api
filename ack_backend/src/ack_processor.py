import json
import logging
from datetime import datetime
from log_structure_splunk import ack_function_info
from log_structure_splunk import send_log_to_firehose
from update_ack_file import update_ack_file, create_ack_data

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")


# firehose_logger = FirehoseLogger()


@ack_function_info
def lambda_handler(event, context):
    try:
        array_of_rows = []
        for record in event["Records"]:
            incoming_message_body = json.loads(record["body"])
            for message in incoming_message_body:
                # Check if there are any messages to process
                file_key = message.get("file_key")
                row_id = message.get("row_id")
                local_id = message.get("local_id")
                imms_id = message.get("imms_id")
                diagnostics = message.get("diagnostics")
                created_at_formatted_string = message.get("created_at_formatted_string")
                successful_api_response = diagnostics is None
                row = create_ack_data(
                    created_at_formatted_string, local_id, row_id, successful_api_response, diagnostics, imms_id
                )
                array_of_rows.append(row)
        # TODO: Are we confident that all messages in the event will be for the same file?
        # Do we need a check on each row?
        update_ack_file(file_key, created_at_formatted_string=created_at_formatted_string, ack_data_rows=array_of_rows)
        # Delete the message from the queue

    except Exception as e:

        print(f"Error processing SQS message: {e}")
        log_data = {
            "status": "fail",
            "statusCode": 500,
            "diagnostics": f"Error processing SQS message: {str(e)}",
            "date_time": str(datetime.now()),
            "error_source": "ack_lambda_handler",
        }
        send_log_to_firehose(log_data)

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
