import responses
import unittest
import json
import base64
from responses import matchers
from unittest.mock import create_autospec, MagicMock, patch, ANY
from pds import PdsService
from pds import Authenticator


class TestPdsService(unittest.TestCase):
    def setUp(self):
        self.authenticator = create_autospec(Authenticator)
        self.access_token = "secret"
        self.authenticator.get_access_token.return_value = self.access_token
        self.pds_service = PdsService(self.authenticator, "int")
        self.url = "https://int.api.service.nhs.uk/personal-demographics/FHIR/R4/Patient"
    
    @responses.activate
    def test_get_patient_details(self):
        patient_id = "900000009"
        act_res = {"id": patient_id}
        exp_header = {
            'Authorization': f'Bearer {self.access_token}'
        }
        responses.add(responses.GET, f"{self.url}/{patient_id}",
                      json=act_res, status=200,
                      match=[matchers.header_matcher(exp_header)])
        patient = self.pds_service.get_patient_details(patient_id)
        self.assertDictEqual(patient, act_res) 
        
    @responses.activate
    def test_get_patient_details_not_found(self):
        patient_id = "900000009"
        responses.add(responses.GET, f"{self.url}/{patient_id}", status=400)
        patient = self.pds_service.get_patient_details(patient_id)
        self.assertIsNone(patient) 
        

class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        self.secret_manager_client = MagicMock()
        self.kid = "a_kid"
        self.api_key = "an_api_key"
        self.private_key = "a_private_key"
        self.secret_response = {"private_key": base64.b64encode(self.private_key.encode()).decode(), "kid": self.kid, "api_key": self.api_key}
        self.secret_manager_client.get_secret_value.return_value = {"SecretString": json.dumps(self.secret_response)}
        self.authenticator = Authenticator(self.secret_manager_client, "int")
        self.url = "https://int.api.service.nhs.uk/oauth2/token"

    @responses.activate
    def test_get_access_token(self):
        jwt_secret = "secret"
        access_token = "54321"
        token_data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': jwt_secret
        }
        responses.add(responses.POST, self.url, status=200, json={"access_token": access_token},
                      match=[matchers.urlencoded_params_matcher(token_data)])
        with patch("jwt.encode") as mock_jwt:
            mock_jwt.return_value = jwt_secret
            act_access_token = self.authenticator.get_access_token()
            mock_jwt.assert_called_once_with(ANY, ANY, algorithm="RS512", headers={"kid": ANY})
            self.assertEqual(act_access_token, access_token)

    @responses.activate
    def test_jwt_values(self):
        claims = {
            "iss": self.api_key,
            "sub": self.api_key,
            "aud": self.url,
            "iat": ANY,
            "exp": ANY,
            "jti": ANY
        }
        jwt_secret = "secret"
        access_token = "54321"
        responses.add(responses.POST, self.url, status=200, json={"access_token": access_token})
        with patch("jwt.encode") as mock_jwt:
            mock_jwt.return_value = jwt_secret
            self.authenticator.get_access_token()
            mock_jwt.assert_called_once_with(claims, self.private_key, algorithm="RS512", headers={"kid": self.kid})



if __name__ == '__main__':
    unittest.main()
