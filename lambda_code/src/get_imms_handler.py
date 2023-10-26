from dynamodb import EventTable
import json


def get_imms_handler(event, context):
    event_body = json.dumps(event)
    print(event_body)
    event_id = event["pathParameters"]["id"]
    dynamo_service = EventTable()
    message = dynamo_service.get_event_by_id(event_id)
    response = {
        "statusCode": 200,  # HTTP status code
        "body": json.dumps({
            "message": message  
        })
    }
    return response
