#!/Users/ewan.childs/Desktop/NHS/Bebop/immunisation-fhir-api/.venv/bin/python3.9
import uuid
import time
import requests
import os
import jwt


class PdsService:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.key_file_path = os.path.join(self.script_dir, "./private_test_1.key")
        self.ENV = "internal-dev"
        with open(self.key_file_path, "rb") as key_file:
            self.private_key = key_file.read()
        self.api_key = "3fZXYrsp9zvwDqayTrsAeH39pSWrmGwX"
        self.kid = "test_1"
        
    def get_access_token(self):
        current_timestamp = int(time.time())
        claims = {
            "iss": self.api_key,
            "sub": self.api_key,
            "aud": f"https://{self.ENV}.api.service.nhs.uk/oauth2/token",
            "iat": current_timestamp,
            "exp": current_timestamp + 30,  # 30 seconds expiry
            "jti": str(uuid.uuid4())
        }
        jwt_token = jwt.encode(claims, self.private_key, algorithm='RS512', headers={"kid": self.kid})
        token_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': jwt_token
        }
        token_response = requests.post(
            f"https://{self.ENV}.api.service.nhs.uk/oauth2/token",
            data=token_data,
            headers=token_headers
        )
        return token_response.json().get('access_token')

    def get_patient_details(self, patient_id):
        access_token = self.get_access_token()
        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Request-ID': str(uuid.uuid4()),
            'X-Correlation-ID': str(uuid.uuid4())
        }
        response = requests.get(f"https://{self.ENV}.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/{patient_id}",
                                headers=request_headers)
        if response.status_code == 200:
            return response
        else:
            return None

# Usage example:
# pds_service = PdsService()
# access_token = pds_service.get_access_token()
# print(access_token)

# patient_id = 9693632109
# response = pds_service.get_patient_details(patient_id)
# print(response)