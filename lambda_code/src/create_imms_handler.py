import json
from dynamodb import EventTable
from get_secret import SecretsManagerSecret
import boto3


def create_imms_handler(event, context):
    event_body = event["body"]
    secrets_manager_client = boto3.client('secretsmanager')
    secret_service = SecretsManagerSecret(secrets_manager_client)
    secret = secret_service.get_value()
    print(event_body)
    print(secret)
    dynamo_service = EventTable()
    message = dynamo_service.put_event(event_body)
    response = {
        "statusCode": 201,
        "body": json.dumps({
            "message": message  
        })
    }
    return response
