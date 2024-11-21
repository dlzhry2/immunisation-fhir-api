import json
from update_ack_file import update_ack_file


def lambda_handler(event, context):

    try:
        imms_id = None
        successful_api_response= True
        print(f"event: {event}")
        for record in event["Records"]:
            body_json = record['body']
            incoming_message_body = json.loads(body_json) 
            # Check if there are any messages to process
            file_key = incoming_message_body.get("file_key")
            row_id = incoming_message_body.get("row_id")
            diagnostics = incoming_message_body.get("diagnostics")
            created_at_formatted_string = incoming_message_body.get("created_at_formatted_string")
            if diagnostics is None:
                status_code = incoming_message_body.get('statusCode', 0)
                if status_code not in {200, 201, 204}:
                    # Parse the nested body and extract diagnostics
                    inner_body = json.loads(incoming_message_body.get('body', '{}'))
                    diagnostics = inner_body.get('issue', [{}])[0].get('diagnostics')
            if diagnostics:
                    successful_api_response= False

            # print(f"file_key:{file_key};row_id:{row_id} ")
            # Check the status code and extract the location URL and imms_id if statusCode is 201
            if "statusCode" in incoming_message_body:
                if incoming_message_body['statusCode'] == 201:
                    location_url = incoming_message_body['headers']['Location']
                    imms_id = location_url.split('/')[-1]
                
            update_ack_file(
                file_key,
                row_id,
                successful_api_response=successful_api_response,
                diagnostics=diagnostics,
                imms_id=imms_id,
                created_at_formatted_string=created_at_formatted_string
            )
            # Delete the message from the queue

    except Exception as e:
        print(f"Error processing SQS message: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Lambda function executed successfully!"),
    }
