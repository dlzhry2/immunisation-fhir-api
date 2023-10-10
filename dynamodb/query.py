import json

import boto3
from boto3.dynamodb.conditions import Key


class EventTable:
    def __init__(self, endpoint_url, table_name):
        db = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        self.table = db.Table(table_name)

    def get_event_by_id(self, id):
        response = self.table.get_item(Key={'Id': id})
        if 'Item' in response:
            return json.loads(response['Item']["Event"])
        else:
            return None

    def get_patient(self, nhs_number):
        response = self.table.query(
            IndexName='NhsNumber',
            KeyConditionExpression=Key('NhsNumber').eq(nhs_number)
        )

        if 'Items' in response:
            return response['Items']
        else:
            return None

    def put_event(self, event):
        response = self.table.put_item(Item={
            'Id': event["identifier"][0]["value"],
            'Event': json.dumps(event),
            'NhsNumber': event["patient"]["identifier"][0]["value"],
            'PatientDob': event["patient"]["birthDate"]
        })
        return event if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    def delete_event(self, event_id):
        response = self.table.delete_item(Key={"Id": event_id})
        return event_id if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None


DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "Events3"

if __name__ == '__main__':
    table = EventTable(DYNAMODB_URL, TABLE_NAME)
    # event = table.get_event_by_id("ff6be98e-fbbe-4c33-b5fe-153a13920519")
    # event = table.get_patient_by_nhs_number("111111111")
    # event = table.get_event_by_id("fsdfd")
    event = table.delete_event("136dbac8-5f48-475d-80ab-6d936832c349")
    print(event)
