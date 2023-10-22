import json

import boto3
from boto3.dynamodb.conditions import Key


class EventTable:
    def __init__(self, endpoint_url, table_name):
        db = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        self.table = db.Table(table_name)

    def get_event_by_id(self, event_id):
        # TODO: the main index doesn't need sort-key. You can use get_item instead of query
        response = self.table.get_item(Key={'PK': event_id})

        if 'Item' in response:
            return json.loads(response['Item']["Event"])
        else:
            return None

    def get_patient(self, nhs_number, parameters=None):
        condition = Key('PatientPK').eq(nhs_number)

        if parameters and "dateOfBirth" in parameters:
            if "diseaseType" in parameters:
                sort_key = f"{parameters['dateOfBirth']}#{parameters['diseaseType']}"
                condition &= Key('PatientSK').begins_with(sort_key)
            else:
                condition &= Key('PatientSK').begins_with(parameters["dateOfBirth"])

        response = self.table.query(
            IndexName='PatientGSI',
            KeyConditionExpression=condition,
        )

        if 'Items' in response:
            return response['Items']
        else:
            return None

    def put_event(self, event):
        # TODO: change all explicit array indices to filter
        event_id = event["identifier"][0]["value"]

        patient_id = event["patient"]["identifier"][0]["value"]
        patient_dob = event["patient"]["birthDate"]
        local_patient_id = event["contained"][0]["item"][3]["answer"][0]["valueCoding"]["code"]
        local_patient_uri = event["contained"][0]["item"][3]["answer"][0]["valueCoding"]["system"]

        disease_type = event["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]
        vaccine_type = event["vaccineCode"]["coding"][0]["code"]
        vaccine_procedure_code = event["extension"][0]["valueCodeableConcept"]["coding"][0]["code"]

        pk = event_id

        patient_pk = patient_id
        patient_sk = f"{patient_dob}#{disease_type}#{event_id}"

        response = self.table.put_item(Item={
            'PK': pk,
            'Event': json.dumps(event),
            'PatientPK': patient_pk,
            'PatientSK': patient_sk,
        })
        return event if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None

    def delete_event(self, event_id):
        response = self.table.delete_item(Key={"PK": event_id})
        return event_id if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else None


DYNAMODB_URL = "http://localhost:8000"
TABLE_NAME = "Imms"

if __name__ == '__main__':
    table = EventTable(DYNAMODB_URL, TABLE_NAME)
    # event = table.get_event_by_id("ff6be98e-fbbe-4c33-b5fe-153a13920519")
    # event = table.get_patient_by_nhs_number("111111111")
    # event = table.get_event_by_id("fsdfd")
    event2 = table.delete_event("136dbac8-5f48-475d-80ab-6d936832c349")
    print(event2)
