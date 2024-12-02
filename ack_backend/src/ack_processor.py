import json
from update_ack_file import update_ack_file, create_ack_data


def lambda_handler(event, context):

    try:
        imms_id = None
        successful_api_response = True
        array_of_rows = []
        for record in event["Records"]:
            body_json = record["body"]
            incoming_message_body = json.loads(body_json)
            for item in incoming_message_body: 
                # Check if there are any messages to process
                file_key = item.get("file_key")
                row_id = item.get("row_id")
                local_id = item.get("local_id")
                imms_id = item.get("imms_id")
                diagnostics = item.get("diagnostics")
                created_at_formatted_string = item.get(
                    "created_at_formatted_string"
                )
                if diagnostics is None:
                    successful_api_response = True
                else:
                    successful_api_response = False
                row = create_ack_data(created_at_formatted_string, local_id, row_id, successful_api_response, diagnostics, imms_id)
                array_of_rows.append(row)
        update_ack_file(
            file_key,
            created_at_formatted_string=created_at_formatted_string,
            ack_data_rows=array_of_rows
        )
        # Delete the message from the queue

    except Exception as e:
        print(f"Error processing SQS message: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
