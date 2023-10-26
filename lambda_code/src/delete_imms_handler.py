import json
from dynamodb import EventTable


def delete_imms_handler(event, context):
    event_body = json.dumps(event)
    print(event_body)
    event_id = event["pathParameters"]["id"]
    dynamo_service = EventTable()
    message = dynamo_service.delete_event(event_id)
    response = {
            "statusCode": 200,  # HTTP status code
            "body": json.dumps({
                "message": message  
            })
        }
    return response
