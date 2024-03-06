import boto3
import json
from botocore.config import Config
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
import os
from datetime import datetime, timedelta

def get_delta_table(table_name, region_name="eu-west-2"):
    config = Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1})
    db: DynamoDBServiceResource = boto3.resource(
        "dynamodb", region_name=region_name, config=config
    )
    return db.Table(table_name)


def query():
     #Query for finding multiple records b/w two Datetimestamp with multiple Operation
        operations = ['CREATE']
        start_timestamp = '2024-03-06T13:30:20'
        end_timestamp = '2024-03-06T13:33:54'
        results = []

        for operation in operations:
            expression_attribute_values = {
                ':start': start_timestamp,
                ':end': end_timestamp,
                ':operation': operation
            }

            key_condition_expression = 'Operation = :operation AND DateTimeStamp BETWEEN :start AND :end'
            delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
            response = delta_table.query(
                IndexName="SearchIndex",
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            print(response)
            results.extend(response['Items'])

        return results
'''
def scan_records():
    operation = ['DELETE']
    start_prefix = '2024-03-01T14:50:16'
    end_prefix = '2024-03-01T14:56:44'
    delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
    response = delta_table.scan(
        FilterExpression='begins_with(DateTimeStamp, :start) AND begins_with(DateTimeStamp, :end) AND Operation = :operation',
        ExpressionAttributeValues={
            ':start': start_prefix,
            ':end': end_prefix,
            ':operation': operation,
        }
    )

    return response['Items']

'''
def handler(event, context):
    try:
        #delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
        delta_table = get_delta_table(os.environ["DELTA_TABLE_NAME"])
        delta_source = os.environ["SOURCE"]
        #Converting ApproximateCreationDateTime directly to string will give Unix timestamp
        #I am converting it to isofformat for filtering purpose. This can be changed accordingly

        for record in event['Records']:
            approximate_creation_time = datetime.utcfromtimestamp(record['dynamodb']['ApproximateCreationDateTime'])
            expiry_time=approximate_creation_time+ timedelta(minutes=1)
            expiry_time_epoch = int(expiry_time.timestamp())
            print("expiry time",expiry_time)
            print("expiry_time_epoch",expiry_time_epoch)
            new_image = record['dynamodb']['NewImage']
            print(new_image)
            imms_id = new_image['PK']['S'].split("#")[1]
            response = delta_table.put_item(Item={
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