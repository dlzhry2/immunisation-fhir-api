import uuid
from dataclasses import dataclass
from enum import Enum
from time import time
from urllib.parse import urlparse, parse_qs

import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from lxml import html


@dataclass
class AuthenticationError(RuntimeError):
    message: str


class AuthType(str, Enum):
    APP_RESTRICTED = "ApplicationRestricted"
    NHS_LOGIN = "NhsLogin"
    CIS2 = "Cis2"


@dataclass
class AppRestrictedConfig:
    client_id: str
    kid: str
    private_key_content: str
    expiry_seconds: int = 30


class AppRestrictedAuthentication:
    def __init__(self, auth_url: str, config: AppRestrictedConfig):
        self.expiry = config.expiry_seconds
        self.private_key = config.private_key_content
        self.client_id = config.client_id
        self.kid = config.kid
        self.token_url = f"{auth_url}/token"

    def get_access_token(self):
        now = int(time())
        claims = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.token_url,
            "iat": now,
            "exp": now + self.expiry,
            "jti": str(uuid.uuid4())
        }
        _jwt = jwt.encode(claims, self.private_key, algorithm='RS512', headers={"kid": self.kid})

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': _jwt
        }
        token_response = requests.post(self.token_url, data=data, headers=headers)

        if token_response.status_code != 200:
            raise AuthenticationError(f"ApplicationRestricted token POST request failed\n{token_response.text}")

        return token_response.json().get('access_token')


class IntNhsLoginMockAuth:

    def __init__(self, apigee_env, auth_data: dict) -> None:
        self.auth_data = auth_data
        base_url = f"https://{apigee_env}.api.service.nhs.uk/oauth2-mock"
        self.auth_url = f"{base_url}/authorize"
        self.token_url = f"{base_url}/token"

    @staticmethod
    def extract_code(response) -> str:
        qs = urlparse(
            response.history[-1].headers["Location"]
        ).query
        auth_code = parse_qs(qs)["code"]
        if isinstance(auth_code, list):
            # in case there's multiple, this was a bug at one stage
            auth_code = auth_code[0]

        return auth_code

    @staticmethod
    def extract_form_url(response) -> str:
        html_str = response.content.decode()
        tree = html.fromstring(html_str)
        authorize_form = tree.forms[0]

        return authorize_form.action

    def get_token(self) -> str:
        login_session = requests.session()

        client_id = self.auth_data["client_id"]
        client_secret = self.auth_data["client_secret"]
        callback_url = self.auth_data["callback_url"]
        scope = self.auth_data["scope"]
        username = self.auth_data["username"]

        # Step1: login page
        authorize_resp = login_session.get(
            self.auth_url,
            params={
                "client_id": client_id,
                "redirect_uri": callback_url,
                "response_type": "code",
                "scope": scope,
                "state": "1234567890",
            },
        )

        # Step2: Submit login form
        form_action_url = self.extract_form_url(authorize_resp)
        form_submission_data = {"username": username}
        code_resp = login_session.post(url=form_action_url, data=form_submission_data)

        # Step3: extract code form redirect
        auth_code = self.extract_code(code_resp)

        # Step4: Post the code to get access token
        token_resp = login_session.post(
            self.token_url,
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": callback_url,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )

        return token_resp.json()["access_token"]


class KeyManager:
    _key_size = 4096

    def __init__(self, key_id: str):
        self.key_id = key_id

    def gen_private_public_pem(self) -> (bytes, bytes):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self._key_size
        )
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())

        public_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)

        return private_key_pem, public_key_pem

    def write(self, private, public):
        private_key_file = open(f"{self.key_id}.pem", "w")
        private_key_file.write(private.decode())
        private_key_file.close()

        public_key_file = open(f"{self.key_id}.pub", "w")
        public_key_file.write(public.decode())
        public_key_file.close()


if __name__ == '__main__':
    km = KeyManager("mykey")
    (prv, pub) = km.gen_private_public_pem()
    km.write(prv, pub)
