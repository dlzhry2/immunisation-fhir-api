import json
import os
import time
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Attr


def create_table(table_name=None, endpoint_url=None):
    if not table_name:
        table_name = os.environ["DYNAMODB_TABLE_NAME"]
    db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name='eu-west-2')
    return db.Table(table_name)


class ImmunisationRepository:
    def __init__(self, table):
        self.table = table

    def get_immunization_by_id(self, imms_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={"PK": self._make_id(imms_id)})

        if "Item" in response:
            return json.loads(response["Item"]["Resource"])
        else:
            return None

    def create_immunization(self, imms):
        pk = self._make_id(imms["id"])

        response = self.table.put_item(Item={
            'PK': pk,
            'Resource': json.dumps(imms),
        })

        return imms if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    def delete_immunization(self, imms_id: str) -> Optional[str]:
        epoch_time = int(time.time())
        response = self.table.update_item(
            Key={'PK': self._make_id(imms_id)},
            UpdateExpression='SET DeletedAt = :timestamp',
            ExpressionAttributeValues={
                ':timestamp': epoch_time,
            },
            ConditionExpression=Attr("DeletedAt").not_exists()
        )
        return imms_id if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    @staticmethod
    def _make_id(_id):
        return f"Immunization#{_id}"
