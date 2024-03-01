import boto3
import json
from botocore.config import Config
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
import os
from datetime import datetime

def get_delta_table(table_name, region_name="eu-west-2"):
    config = Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1})
    db: DynamoDBServiceResource = boto3.resource(
        "dynamodb", region_name=region_name, config=config
    )
    return db.Table(table_name)

def handler(event, context):
    
    delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
    delta_source = os.environ["SOURCE"]
    print(delta_table)

    #Converting ApproximateCreationDateTime directly to string will give Unix timestamp
    #I am converting it to isofformat for filtering purpose. This can be changed accordingly

    for record in event['Records']:
        approximate_creation_time = datetime.utcfromtimestamp(record['dynamodb']['ApproximateCreationDateTime'])
        new_image = record['dynamodb']['NewImage']
        print(new_image)
        response = delta_table.put_item(Item={
            'Operation': "CREATE",
            'DateTimeStamp' : approximate_creation_time.isoformat(),
            'Source' : delta_source,
            'Imms' : new_image['Resource']['S']
        })

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                print("Record Successfullyl created")
        else:
                print("NOT created")  
    return {
            'statusCode': 200,
            'body': json.dumps('Records processed successfully and tested')
    }
