import json

import boto3


class EventTable:
    def __init__(self, endpoint_url, table_name):
        db = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        self.table = db.Table(table_name)

    def get_event_by_id(self, id):
        response = self.table.get_item(Key={'Id': id})
        if 'Item' in response:
            item = response['Item']["Event"]
            return item
        else:
            return None

    def put_event(self, event):
        self.table.put_item(Item={
            'Id': event["identifier"][0]["value"],
            'Event': json.dumps(event)
        })


DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "imms-events"

if __name__ == '__main__':
    table = EventTable(DYNAMODB_URL, TABLE_NAME)
    event = table.get_event_by_id("9a5448ca-bca4-4815-b3bc-f64fd56f7336")
    event = table.get_event_by_id("fsdfd")
    print(event)
