from dynamodb import EventTable
import json


def delete_imms_handler(event, context):
    event_body = json.dumps(event)
    print(event_body)
    event_id = event["pathParameters"]["id"]
    dynamo_service = EventTable()
    message = dynamo_service.delete_event(event_id)

    return message
