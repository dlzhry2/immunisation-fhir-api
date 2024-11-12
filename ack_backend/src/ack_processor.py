import json
from update_ack_file import update_ack_file


def lambda_handler(event, context):

    try:
        print(f"event: {event}")
        for record in event["Records"]:
            body_json = record['body']
            incoming_message_body = json.loads(body_json)
            # Check if there are any messages to process
            file_key = incoming_message_body.get("Filename")
            row_id = incoming_message_body.get("MessageId")
            print(f"file_key:{file_key};row_id:{row_id} ")
            location_url = incoming_message_body['headers']['Location']
            imms_id = location_url.split('/')[-1]
            update_ack_file(
                file_key,
                row_id,
                successful_api_response=True,
                diagnostics=None,
                imms_id=imms_id,
            )
        # Delete the message from the queue

    except Exception as e:
        print(f"Error processing SQS message: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
