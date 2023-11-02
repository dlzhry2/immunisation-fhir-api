import json
import os

import boto3
from boto3.dynamodb.conditions import Key


class EventTable:
    def __init__(self, table_name=os.environ["DYNAMODB_TABLE_NAME"], endpoint_url=None):
        db = boto3.resource("dynamodb", endpoint_url=endpoint_url, region_name='eu-west-2')
        self.table = db.Table(table_name)

    def get_event_by_id(self, event_id):
        # TODO: the main index doesn't need sort-key. You can use get_item instead of query
        response = self.table.get_item(Key={"PK": event_id})

        if "Item" in response:
            return json.loads(response["Item"]["Event"])
        else:
            return None

    def get_patient(self, nhs_number, parameters=None):
        condition = Key("PatientPK").eq(nhs_number)

        if parameters and "dateOfBirth" in parameters:
            if "diseaseType" in parameters:
                sort_key = f"{parameters['dateOfBirth']}#{parameters['diseaseType']}"
                condition &= Key("PatientSK").begins_with(sort_key)
            else:
                condition &= Key("PatientSK").begins_with(parameters["dateOfBirth"])

        response = self.table.query(
            IndexName="PatientGSI",
            KeyConditionExpression=condition,
        )

        if "Items" in response:
            return response["Items"]
        else:
            return None

    def put_event(self, event):
        # TODO: change all explicit array indices to filter
        event_id = event["identifier"][0]["value"]

        patient_id = event["patient"]["identifier"][0]["value"]
        patient_dob = event["patient"]["birthDate"]

        disease_type = event["protocolApplied"][0]["targetDisease"][0]["coding"][0][
            "code"
        ]

        pk = event_id

        patient_pk = patient_id
        patient_sk = f"{patient_dob}#{disease_type}#{event_id}"

        response = self.table.put_item(
            Item={
                "PK": pk,
                "Event": json.dumps(event),
                "PatientPK": patient_pk,
                "PatientSK": patient_sk,
            }
        )
        return event if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    def delete_event(self, event_id):
        response = self.table.delete_item(Key={"PK": event_id})
        return (
            event_id if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None
        )
