from dynamodb import EventTable
from validation import validate
import json


def get_imms_handler(event, context):
    print(f"from get imms handler {validate()}")

    event_body = json.dumps(event)
    print(event_body)
    event_id = event["pathParameters"]["id"]
    dynamo_service = EventTable()
    message = dynamo_service.get_event_by_id(event_id)

    return message
