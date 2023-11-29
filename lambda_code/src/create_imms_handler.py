from pds import PdsService


def create_imms_handler(event, context):
    event_body = event["body"]
    nhs_number = event_body["nhs_number"]
    pds_service = PdsService()
    patient_response = pds_service.get_patient_details(nhs_number)
    print(patient_response, "<<<<<<<<<<<, PATIENT_RESPONSE")
    print(event_body, "<<<<<<<<<<<< EVENT_BODY")