import json
import os
import time
from typing import Optional

import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Attr

from models.errors import ResourceNotFoundError, UnhandledResponseError


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
            return None if "DeletedAt" in response["Item"] else json.loads(response["Item"]["Resource"])
        else:
            return None

    def create_immunization(self, immunization: dict) -> Optional[dict]:
        pk = self._make_id(immunization["id"])

        response = self.table.put_item(Item={
            'PK': pk,
            'Resource': json.dumps(immunization),
        })

        return immunization if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    def delete_immunization(self, imms_id: str) -> dict:
        now_timestamp = int(time.time())
        try:
            response = self.table.update_item(
                Key={'PK': self._make_id(imms_id)},
                UpdateExpression='SET DeletedAt = :timestamp',
                ExpressionAttributeValues={
                    ':timestamp': now_timestamp,
                },
                ReturnValues="ALL_NEW",
                ConditionExpression=Attr("PK").eq(self._make_id(imms_id)) & Attr("DeletedAt").not_exists()
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return json.loads(response["Attributes"]["Resource"])
            else:
                raise UnhandledResponseError(message="Non-200 response from dynamodb", response=response)

        except botocore.exceptions.ClientError as e:
            # Either resource didn't exist or it has already been deleted. See ConditionExpression in the request
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ResourceNotFoundError(resource_type="Immunization", resource_id=imms_id)
            else:
                raise UnhandledResponseError(message=f"Unhandled error from dynamodb: {e.response['Error']['Code']}",
                                             response=e.response)

    @staticmethod
    def _make_id(_id):
        return f"Immunization#{_id}"
