from pds_repository import PdsRepository

class PdsService:
    
    def __init__(self, pds_repo: PdsRepository):
        self.pds_repo = pds_repo
        
    def get_patient_by_id(self, patient_id: str):
        patient = self.pds_repo.get_pds_patient(patient_id)
        if patient:
            return patient
        else:
            return None

    
        