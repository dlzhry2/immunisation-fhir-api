import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from time import time

import jwt
import requests


@dataclass
class AuthenticationError(RuntimeError):
    message: str


class AuthType(str, Enum):
    APP_RESTRICTED = "ApplicationRestricted"
    NHS_LOGIN = "NhsLogin"
    CIS2 = "Cis2"


class BaseAuthentication(ABC):
    """interface for Apigee app authentication. ApigeeService uses this to get access token"""

    @abstractmethod
    def get_access_token(self):
        pass


@dataclass
class AppRestrictedCredentials:
    client_id: str
    kid: str
    private_key_content: str
    expiry_seconds: int = 30


class AppRestrictedAuthentication(BaseAuthentication):
    def __init__(self, auth_url: str, config: AppRestrictedCredentials):
        self.expiry = config.expiry_seconds
        self.private_key = config.private_key_content
        self.client_id = config.client_id
        self.kid = config.kid
        self.token_url = f"{auth_url}/token"

    def __str__(self):
        return AuthType.APP_RESTRICTED.value

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


class NhsLoginAuthentication(BaseAuthentication):
    def get_access_token(self):
        # TODO(NhsLogin_AMB-1923) add NHSLogin
        pass


class Cis2Authentication(BaseAuthentication):
    def get_access_token(self):
        # TODO(Cis2_AMB-1733) add Cis2
        pass

# def get_access_token_via_user_restricted_flow_separate_auth(
#     identity_service_base_url,
#     keycloak_client_credentials,
#     login_form,
#     apigee_client_id,
#     jwt_private_key,
#     jwt_kid,
#     auth_scope: Literal["nhs-login", "nhs-cis2"],
#     apigee_environment,
# ):
#     if auth_scope == "nhs-cis2":
#         # Get token from keycloak
#         config = KeycloakUserConfig(
#             realm=f"Cis2-mock-{apigee_environment}",
#             client_id=keycloak_client_credentials["cis2"]["client_id"],
#             client_secret=keycloak_client_credentials["cis2"]["client_secret"],
#             login_form=login_form,
#         )
#         authenticator = KeycloakUserAuthenticator(config=config)
#         id_token = authenticator.get_token()["id_token"]
#
#     else:
#         # Get token from keycloak
#         config = KeycloakUserConfig(
#             realm=f"NHS-Login-mock-{apigee_environment}",
#             client_id=keycloak_client_credentials["nhs-login"]["client_id"],
#             client_secret=keycloak_client_credentials["nhs-login"]["client_secret"],
#             login_form=login_form,
#         )
#         authenticator = KeycloakUserAuthenticator(config=config)
#         id_token = authenticator.get_token()["id_token"]
#
#     # Exchange token
#     config = TokenExchangeConfig(
#         environment=apigee_environment,
#         identity_service_base_url=identity_service_base_url,
#         client_id=apigee_client_id,
#         jwt_private_key=jwt_private_key,
#         jwt_kid=jwt_kid,
#         id_token=id_token,
#     )
#     authenticator = TokenExchangeAuthenticator(config=config)
#     return authenticator.get_token()
#
#
