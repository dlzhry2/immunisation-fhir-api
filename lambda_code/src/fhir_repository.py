import json
import os
import time
import uuid
from typing import Optional

import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Attr, Key
from botocore.config import Config

from models.errors import ResourceNotFoundError, UnhandledResponseError


def create_table(table_name=None, endpoint_url=None, region_name='eu-west-2'):
    if not table_name:
        table_name = os.environ["DYNAMODB_TABLE_NAME"]
    config = Config(connect_timeout=1, read_timeout=1)
    db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name=region_name, config=config)
    return db.Table(table_name)


class ImmunizationRepository:
    def __init__(self, table):
        self.table = table

    def get_immunization_by_id(self, imms_id: str) -> Optional[dict]:
        response = self.table.get_item(Key={"PK": self._make_immunization_pk(imms_id)})

        if "Item" in response:
            return None if "DeletedAt" in response["Item"] else json.loads(response["Item"]["Resource"])
        else:
            return None

    def create_immunization(self, immunization: dict) -> dict:
        new_id = str(uuid.uuid4())
        immunization["id"] = new_id

        patient_id = immunization["patient"]["identifier"]["value"]
        # TODO: protocolApplied is not in imms-history example. Is it CSV specific?
        disease_type = immunization["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]

        # TODO: if imms can only have one disease type then do we need to append id at the end?
        patient_sk = f"{disease_type}#{new_id}"

        response = self.table.put_item(Item={
            'PK': self._make_immunization_pk(new_id),
            'Resource': json.dumps(immunization),
            'PatientPK': self._make_patient_pk(patient_id),
            'PatientSK': patient_sk,
        })

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return immunization
        else:
            raise UnhandledResponseError(message="Non-200 response from dynamodb", response=response)

    def delete_immunization(self, imms_id: str) -> dict:
        now_timestamp = int(time.time())
        try:
            response = self.table.update_item(
                Key={'PK': self._make_immunization_pk(imms_id)},
                UpdateExpression='SET DeletedAt = :timestamp',
                ExpressionAttributeValues={
                    ':timestamp': now_timestamp,
                },
                ReturnValues="ALL_NEW",
                ConditionExpression=Attr("PK").eq(self._make_immunization_pk(imms_id)) & Attr("DeletedAt").not_exists()
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

    def find_immunizations(self, nhs_number: str, disease_code: str):
        """it should find all patient's Immunization events for a specified disease_code"""
        condition = Key("PatientPK").eq(self._make_patient_pk(nhs_number))
        sort_key = f"{disease_code}#"
        condition &= Key("PatientSK").begins_with(sort_key)
        is_not_deleted = Attr("DeletedAt").not_exists()

        response = self.table.query(
            IndexName="PatientGSI",
            KeyConditionExpression=condition,
            FilterExpression=is_not_deleted
        )

        if "Items" in response:
            return [json.loads(item["Resource"]) for item in response["Items"]]
        else:
            raise UnhandledResponseError(message=f"Unhandled error. Query failed", response=response)

    @staticmethod
    def _make_immunization_pk(_id: str):
        return f"Immunization#{_id}"

    @staticmethod
    def _make_patient_pk(_id: str):
        return f"Patient#{_id}"
