import os
import json
import boto3

from validation import validate
from dynamodb import EventTable


def search_imms_handler(event, context):
    event_body = json.dumps(event)
    print(event_body)
    nhs_number = event["queryStringParameters"]["NhsNumber"]

    dynamo_service = EventTable()
    message = dynamo_service.get_patient(
        nhs_number, parameters=event["queryStringParameters"]
    )

    return message
