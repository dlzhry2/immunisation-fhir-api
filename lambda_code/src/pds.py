import time
import uuid

import boto3
import jwt
import requests

from get_secret import SecretsManagerSecret


class PdsService:
    def __init__(self):
        secrets_manager_client = boto3.client('secretsmanager')
        secret_service = SecretsManagerSecret(secrets_manager_client)
        self.ENV = "internal-dev"
        self.private_key = secret_service.get_value()
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
