import json
import os
import time
from typing import Optional

import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Attr


def create_table(table_name=None, endpoint_url=None):
    if not table_name:
        table_name = os.environ["DYNAMODB_TABLE_NAME"]
    db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name='eu-west-2')
    return db.Table(table_name)


class ImmunisationRepository:
    def __init__(self, table):
        self.table = table

    def get_immunisation_by_id(self, imms_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={"PK": self._make_id(imms_id)})

        if "Item" in response:
            return json.loads(response["Item"]["Resource"])
        else:
            return None

    def delete_immunisation(self, imms_id: str) -> Optional[str]:
        epoch_time = int(time.time())
        try:
            response = self.table.update_item(
                Key={'PK': self._make_id(imms_id)},
                UpdateExpression='SET DeletedAt = :timestamp',
                ExpressionAttributeValues={
                    ':timestamp': epoch_time,
                },
                ConditionExpression=Attr("DeletedAt").not_exists()
            )
            return imms_id if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise
            else:
                return imms_id

    @staticmethod
    def _make_id(_id):
        return f"Immunization#{_id}"
