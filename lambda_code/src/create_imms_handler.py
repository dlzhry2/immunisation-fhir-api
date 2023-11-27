import json
from dynamodb import EventTable
from pds import PdsService


def create_imms_handler(event, context):
    event_body = event["body"]
    nhs_number = event_body["nhs_number"]
    pds_service = PdsService()
    patient_response = pds_service.get_patient_details(nhs_number)
    print(patient_response, "<<<<<<<<<<<, PATIENT_RESPONSE")
    print(event_body, "<<<<<<<<<<<< EVENT_BODY")
    event_body = json.loads(event["body"])
    dynamo_service = EventTable()
    message = dynamo_service.put_event(event_body)
    response = {
        "statusCode": 201,  # HTTP status code
        "body": json.dumps({
            "message": message  
        })
    }
    return response
