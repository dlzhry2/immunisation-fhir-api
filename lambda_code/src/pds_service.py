import base64
import json
import time
import uuid

import jwt
import requests

from models.errors import UnhandledResponseError


class Authenticator:
    def __init__(self, secret_manager_client, environment):
        self.secret_manager_client = secret_manager_client
        self.secret_name = f"imms/pds/{environment}/jwt-secrets"
        self.token_url = f"https://{environment}.api.service.nhs.uk/oauth2/token" \
            if environment != "prod" else "https://api.service.nhs.uk/oauth2/token"

    def get_pds_secrets(self):
        kwargs = {"SecretId": self.secret_name}
        response = self.secret_manager_client.get_secret_value(**kwargs)
        secret_object = json.loads(response['SecretString'])
        secret_object['private_key'] = base64.b64decode(secret_object['private_key_b64']).decode()

        return secret_object

    def create_jwt(self):
        secret_object = self.get_pds_secrets()
        current_timestamp = int(time.time())
        claims = {
            "iss": secret_object['api_key'],
            "sub": secret_object['api_key'],
            "aud": self.token_url,
            "iat": current_timestamp,
            "exp": current_timestamp + 30,
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(claims, secret_object['private_key'], algorithm='RS512',
                          headers={"kid": secret_object['kid']})

    def get_access_token(self):
        _jwt = self.create_jwt()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': _jwt
        }
        token_response = requests.post(self.token_url, data=data, headers=headers, timeout=2)

        return token_response.json().get('access_token')


class PdsService:
    def __init__(self, authenticator: Authenticator, environment):
        self.authenticator = authenticator

        self.base_url = f"https://{environment}.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient" \
            if environment != "prod" else "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"

    def get_patient_details(self, patient_id):
        access_token = self.authenticator.get_access_token()
        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Request-ID': str(uuid.uuid4()),
            'X-Correlation-ID': str(uuid.uuid4())
        }
        response = requests.get(f"{self.base_url}/{patient_id}", headers=request_headers, timeout=2)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            msg = "Downstream service failed to validate the patient"
            raise UnhandledResponseError(response=response.json(), message=msg)
