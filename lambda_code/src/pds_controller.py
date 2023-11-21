import json

class PdsController:
    def __init__(self, pds_service):
        self.pds_service = pds_service

    def get_patient_details(self, patient_id):
        patient_details = self.pds_service.get_patient_details(patient_id)
        if patient_details:
            response = {
                "statusCode": 200,
                "body": json.dumps(patient_details)
                }
            return response
        else:
            return None
