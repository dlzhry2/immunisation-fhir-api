import json
import os
import time
import uuid
from typing import Optional

import boto3
import botocore.exceptions
from boto3.dynamodb.conditions import Attr, Key

from models.errors import ResourceNotFoundError, UnhandledResponseError


def create_table(table_name=None, endpoint_url=None, region_name='eu-west-2'):
    if not table_name:
        table_name = os.environ["DYNAMODB_TABLE_NAME"]
    db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name=region_name)
    return db.Table(table_name)


class ImmunisationRepository:
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
        # TODO:
        #  Q- Can multiple disease codes be in one Immunizations event? i.e. should disease_code be a list?
        #     A- From word doc it seems all vaccine related info is 0..1 or 1..1 so, I think we can assume it's single
        #  Q- If an event can have multiple diseases then how to we search for a subset of of it?
        #  NOTE: FileterExpression is a good candidate for this since there won't be many imms events
        #  NOTE: Should we store based on diseaseCode or the mapped diseaseType?
        #    I stored it based on the code because, it's what we get in the data
        #    Q- Is it possible for a snomed code to become invalid? If this happens, then storing based on code
        #        instead of diseaseType will result in a record that can never be retrieved via query
        #  FIXME: We know multiple codes can map to a single diseaseType so
        #   1- either we should store the mapped disease type as an attribute and query based on that
        #   2- or, modify the query condition with an OR operation (is it even possible using sort-key?)
        condition = Key("PatientPK").eq(self._make_patient_pk(nhs_number))
        sort_key = f"{disease_code}#"
        condition &= Key("PatientSK").begins_with(sort_key)

        response = self.table.query(
            IndexName="PatientGSI",
            KeyConditionExpression=condition,
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


# TODO: delete me
if __name__ == '__main__':
    table = create_table("local-imms-events", "http://localhost:4566", region_name="us-east-1")
    repo = ImmunisationRepository(table)
    # resp = repo.find_immunizations("dfd", "sdfd")
    resp = repo.find_immunizations("9999999999", "covidCode2")
    # resp = repo.get_immunization_by_id("5a921187-19c7-8df4-8f4f-f31e78de5857")
    print(len(resp))
    print(resp)
