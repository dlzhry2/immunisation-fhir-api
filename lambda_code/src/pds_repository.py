import json
import requests


class PatientRepository:
    def __init__(self, endpoint_url=None):
        self.endpoint_url = "https://internal-dev.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"

class PdsRepository(PatientRepository):
    def get_patient_by_id(self, patient_id: int):
        endpoint_url = f"{self.endpoint_url}/{patient_id}"
        response = requests.get(endpoint_url)

        if "Item" in response:
            return json.loads(response)
        else:
            return None
