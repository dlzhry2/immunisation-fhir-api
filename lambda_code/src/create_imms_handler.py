import json
from dynamodb import EventTable
from get_secret import SecretsManagerSecret
import boto3


def create_imms_handler(event, context):
    event_body = json.loads(event["body"])
    dynamo_service = EventTable()
    message = dynamo_service.put_event(event_body)
    response = {
        "statusCode": 201,  # HTTP status code
        "body": json.dumps({
            "message": message  
        })
    }
    return response
