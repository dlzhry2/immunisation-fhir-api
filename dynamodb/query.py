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

    def get_patient(self, nhs_number, parameters=None):
        condition = Key('NhsNumber').eq(nhs_number)

        if parameters and "dateOfBirth" in parameters:
            condition &= Key('PatientDob').eq(parameters["dateOfBirth"])

        response = self.table.query(
            IndexName='NhsNumber',
            KeyConditionExpression=condition
        )

        if 'Items' in response:
            return response['Items']
        else:
            return None

    def put_event(self, event):
        # TODO: change all explicit array indices to fileter
        event_id = event["identifier"][0]["value"]

        patient_id = event["patient"]["identifier"][0]["value"]
        patient_dob = event["patient"]["birthDate"]
        local_patient_id = event["contained"][0]["item"][3]["answer"][0]["valueCoding"]["code"]
        local_patient_uri = event["contained"][0]["item"][3]["answer"][0]["valueCoding"]["system"]

        disease_type = event["protocolApplied"][0]["targetDisease"][0]["coding"][0]["code"]
        vaccine_type = event["vaccineCode"]["coding"][0]["code"]
        vaccine_procedure_code = event["extension"][0]["valueCodeableConcept"]["coding"][0]["code"]

        pk = event_id
        sk = f""
        patient_pk = patient_id
        patient_sk = f"{patient_dob}#{disease_type}#{event_id}"

        response = self.table.put_item(Item={
            'PK': pk,
            'SK': sk,
            'Event': json.dumps(event),
            'NhsNumber': patient_pk,
            'PatientSK': patient_sk,
            'PatientDob': patient_dob,
            'LocalPatientId': local_patient_id,
            'LocalPatientUri': local_patient_uri,
            'VaccineType': vaccine_type,
            'VaccineProcedureCode': vaccine_procedure_code,
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
