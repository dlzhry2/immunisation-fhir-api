from pds_service import PdsService

class PdsController:
    def __init__(self):
        self.pds_service = PdsService()

    def get_patient_details(self, patient_id):
        return self.pds_service.get_patient_details(patient_id)
