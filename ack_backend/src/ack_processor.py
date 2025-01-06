import json
from datetime import datetime
from log_structure_splunk import ack_function_info
from log_structure_splunk import send_log_to_firehose
from update_ack_file import update_ack_file, create_ack_data


@ack_function_info
def lambda_handler(event, context):
    try:
        array_of_rows = []
        for record in event["Records"]:
            incoming_message_body = json.loads(record["body"])
            file_key = incoming_message_body[0].get("file_key")
            for message in incoming_message_body:
                # Check that the file_key is the same for each message (since each message should be from the same file)
                if message.get("file_key") != file_key:
                    raise ValueError("File key mismatch")
                row_id = message.get("row_id")
                local_id = message.get("local_id")
                imms_id = message.get("imms_id")
                diagnostics = message.get("diagnostics")
                created_at_formatted_string = message.get("created_at_formatted_string")
                successful_response = diagnostics is None  # If diagnostics is None, then the response was successful
                row = create_ack_data(
                    created_at_formatted_string, local_id, row_id, successful_response, diagnostics, imms_id
                )
                array_of_rows.append(row)

            update_ack_file(
                file_key, created_at_formatted_string=created_at_formatted_string, ack_data_rows=array_of_rows
            )

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
