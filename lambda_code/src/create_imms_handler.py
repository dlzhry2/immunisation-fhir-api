import os

import boto3
import json
from dynamodb import EventTable

from validation import validate


def create_imms_handler(event, context):
    print(json.dumps(event))

    dynamo_service = EventTable()
    message = dynamo_service.put_event(json.loads(event["body"]))

    return {"body": message}
