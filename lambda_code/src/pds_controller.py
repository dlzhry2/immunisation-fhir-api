from pds_service import PdsService


class PdsController:

    def __init__(self, pds_service: PdsService):
        self.pds_service = pds_service

    def get_patient_by_id(self, patient_id):
        response = self.pds_service.get_patient_by_id(patient_id)
        if response:
            return PdsController.create_response(200, response.json())
        else:
            return "The requested resource was not found."
