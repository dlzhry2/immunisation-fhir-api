import os

import boto3

from validation import validate


def get_event_handler(event, context):
    message = f"from get event handler {validate()}"
    client = boto3.client('dynamodb')
    table_name = os.environ["DYNAMODB_TABLE_NAME"]
    data = client.scan(
        TableName=table_name
    )
    return {'body': message}
