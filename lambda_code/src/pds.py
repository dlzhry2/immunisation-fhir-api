import uuid
import time
import requests
import jwt
import json
import base64


class Authenticator:
    def __init__(self, secret_manager_client, environment):
        self.secret_manager_client = secret_manager_client
        self.secret_name = 'imms/pds/int/jwt'
        self.environment = environment
        
    def get_value(self):
        kwargs = {"SecretId": self.secret_name}
        response = self.secret_manager_client.get_secret_value(**kwargs)
        secret_object = json.loads(response['SecretString'])
        secret_object['private_key'] = base64.b64decode(secret_object['private_key']).decode()
        return secret_object

    def get_access_token(self):
        secret_object = self.get_value()
        current_timestamp = int(time.time())
        claims = {
            "iss": secret_object['api_key'],
            "sub": secret_object['api_key'],
            "aud": f"https://{self.environment}.api.service.nhs.uk/oauth2/token",
            "iat": current_timestamp,
            "exp": current_timestamp + 30,
            "jti": str(uuid.uuid4())
        }
        jwt_token = jwt.encode(claims, secret_object['private_key'], algorithm='RS512', headers={"kid": secret_object['kid']})
        token_headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': jwt_token
        }
        token_response = requests.post(
            f"https://{self.environment}.api.service.nhs.uk/oauth2/token",
            data=token_data,
            headers=token_headers
        )
        return token_response.json().get('access_token')


class PdsService:
    def __init__(self, authenticator: Authenticator, environment):
        self.authenticator = authenticator
        self.environment = environment

    
    def get_patient_details(self, patient_id):
        access_token = self.authenticator.get_access_token()
        request_headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Request-ID': str(uuid.uuid4()),
            'X-Correlation-ID': str(uuid.uuid4())
        }
        response = requests.get(f"https://{self.environment}.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/{patient_id}",
                                headers=request_headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
