import json
import logging
from typing import Union
from update_ack_file import update_ack_file
from log_structure_splunk import ack_function_info
from log_firehose_splunk import FirehoseLogger

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")


firehose_logger = FirehoseLogger()


@ack_function_info
def lambda_handler(event, context):
    try:
        imms_id = None
        successful_api_response = True
        print(f"event: {event}")
        for record in event["Records"]:
            body_json = record["body"]
            incoming_message_body = json.loads(body_json)
            # Check if there are any messages to process
            file_key = incoming_message_body.get("file_key")
            row_id = incoming_message_body.get("row_id")
            local_id = incoming_message_body.get("local_id")
            imms_id = incoming_message_body.get("imms_id")
            diagnostics = incoming_message_body.get("diagnostics")
            created_at_formatted_string = incoming_message_body.get("created_at_formatted_string")
            if diagnostics is None:
                successful_api_response = True
            else:
                successful_api_response = False

            update_ack_file(
                file_key,
                local_id,
                row_id,
                successful_api_response=successful_api_response,
                diagnostics=diagnostics,
                imms_id=imms_id,
                created_at_formatted_string=created_at_formatted_string,
            )

    except Exception as e:
        print(f"Error processing SQS message: {e}")
        log_data = {
            "status": "fail",
            "statusCode": 500,
            "diagnostics": f"Error processing SQS message: {str(e)}",
            "error_source": "lambda_handler",
        }
        firehose_log = dict()
        firehose_log["event"] = log_data
        firehose_logger.ack_send_log(firehose_log)

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
