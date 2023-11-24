import json

import boto3

sample_file = "sample_data/2023-11-09T19:09:23_immunisation-30.json"

dynamodb_url = "http://localhost:4566"
table_name = "local-imms-events"


class DynamoTable:
    def __init__(self, endpoint_url, _table_name):
        db = boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name="us-east-1")
        self.table = db.Table(_table_name)

    def create_immunization(self, imms):
        imms_id = imms["id"]
        pk = f"Immunization#{imms_id}"

        response = self.table.put_item(Item={
            'PK': pk,
            'Resource': json.dumps(imms),
        })
        return imms if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None


def seed_immunization(table, _sample_file):
    with open(_sample_file, "r") as raw_data:
        imms_list = json.loads(raw_data.read())

    for imms in imms_list:
        table.create_immunization(imms)

    print(f"{len(imms_list)} resources added successfully")


if __name__ == '__main__':
    _table = DynamoTable(dynamodb_url, table_name)
    seed_immunization(_table, sample_file)
