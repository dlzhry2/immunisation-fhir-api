from dynamodb import EventTable
from validation import validate


def get_imms_handler(event, context):
    print(f"from get imms handler {validate()}")

    dynamo_service = EventTable()
    message = dynamo_service.get_event_by_id("event-id")

    return {'body': message}
