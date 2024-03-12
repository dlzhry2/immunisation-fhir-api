import boto3
import json
from botocore.config import Config
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
import os
from datetime import datetime, timedelta
import uuid

def get_delta_table(table_name, region_name="eu-west-2"):
    config = Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1})
    db: DynamoDBServiceResource = boto3.resource(
        "dynamodb", region_name=region_name, config=config
    )
    return db.Table(table_name)


def handler(event, context):
    try:
        delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
        delta_source = os.environ["SOURCE"]
        #Converting ApproximateCreationDateTime directly to string will give Unix timestamp
        #I am converting it to isofformat for filtering purpose. This can be changed accordingly

        for record in event['Records']:
            approximate_creation_time = datetime.utcfromtimestamp(record['dynamodb']['ApproximateCreationDateTime'])
            expiry_time=approximate_creation_time+ timedelta(days=30)
            expiry_time_epoch = int(expiry_time.timestamp())
            new_image = record['dynamodb']['NewImage']
            imms_id = new_image['PK']['S'].split("#")[1]
            response = delta_table.put_item(Item={
                'PK' : str(uuid.uuid4()),
                'ImmsID' :imms_id,
                'Operation': new_image['Operation']['S'],
                'DateTimeStamp' : approximate_creation_time.isoformat(),
                'Source' : delta_source,
                'Imms' : new_image['Resource']['S'],
                'ExpiresAt' : expiry_time_epoch
            })
            
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    print("Record Successfullyl created")
            else:
                    print("NOT created")  
        return {
                'statusCode': 200,
                'body': json.dumps('Records processed successfully and tested')
        }
    
    except Exception as e:
        # Send the failed event to the DLQ
        print("Came in exception")
        print(e)
        '''
        print(event)
        sqs = boto3.client('sqs')
        sqs_queue_url = os.environ.get("DELTA_DEAD_LETTER_QUEUE_URL")
        print(sqs_queue_url)
        sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(event),
        )
        print("Msg sent successful")
        raise e
        '''