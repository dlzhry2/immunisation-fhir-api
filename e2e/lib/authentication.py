import base64
import uuid
from dataclasses import dataclass
from enum import Enum
from time import time
from urllib.parse import urlparse, parse_qs

import jwt
import requests
from authlib.jose import jwk
from cryptography.hazmat.backends import default_backend
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
class AppRestrictedCredentials:
    client_id: str
    kid: str
    private_key_content: str
    expiry_seconds: int = 30


class JwkKeyPair:
    private_key: str
    public_key: str
    key_id: str
    _encoded_n: str = None

    def __init__(self, key_id: str, private_key_path: str = None, public_key_path: str = None):
        self.key_id = key_id

        if private_key_path is None and public_key_path is None:
            self.private_key, self.public_key, self._encoded_n = make_key_pair_n()
        else:
            with open(private_key_path, "r") as private_key:
                self.private_key = private_key.read()
            with open(public_key_path, "r") as public_key:
                self.public_key = public_key.read()

    def make_jwk(self) -> dict:
        new_key = jwk.dumps(self.public_key, kty="RSA", crv_or_size=4096, alg="RS512")
        new_key["kid"] = self.key_id
        new_key["use"] = "sig"

        return new_key

    def make_jwk2(self) -> dict:
        if not self._encoded_n:
            pub_key = serialization.load_pem_public_key(self.public_key.encode(), backend=default_backend())
            n = pub_key.public_numbers().n
            n_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
            self._encoded_n = base64.urlsafe_b64encode(n_bytes).decode('utf-8')

        return {
            "kty": "RSA",
            "n": self._encoded_n,
            "e": "AQAB",
            "alg": "RS512",
            "kid": self.key_id
        }


def make_key_pair_n(key_size=4096) -> (str, str, str):
    # TODO: it's identity service cache causing issue.
    # private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size, backend=default_backend())

    prv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())

    # pub_key = private_key.public_key()
    pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1)

    # n = private_key.public_key().public_numbers().n
    # n_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
    # n_encoded = base64.urlsafe_b64encode(n_bytes).decode('utf-8')

    # pub_key = serialization.load_pem_public_key(pub, backend=default_backend())
    # n = pub_key.public_numbers().n
    n = private_key.public_key().public_numbers().n
    n_bytes = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')
    n_encoded = base64.urlsafe_b64encode(n_bytes).decode('utf-8')

    return prv.decode(), pub.decode(), n_encoded


class AppRestrictedAuthentication:
    def __init__(self, auth_url: str, config: AppRestrictedCredentials):
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
