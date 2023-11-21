import json
from dynamodb import EventTable


def create_imms_handler(event, context):
    print(json.dumps(event))
    event_body = json.loads(event["body"])
    print(event_body)
    dynamo_service = EventTable()
    message = dynamo_service.put_event(event_body)
    response = {
        "statusCode": 201,
        "body": json.dumps({
            "message": message  
        })
    }
    return response
