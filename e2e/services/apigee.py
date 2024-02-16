import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

import requests

from .env import apigee_access_token


class ApigeeOrg(str, Enum):
    PROD = "nhsd-prod"
    NON_PROD = "nhsd-nonprod"


class ApigeeEnv(str, Enum):
    INTERNAL_DEV = "internal-dev"
    SANDBOX = "sandbox"
    INT = "int"


@dataclass
class ApigeeError(RuntimeError):
    message: str


@dataclass
class ApigeeConfig:
    username: str = None
    access_token: str = None
    env: ApigeeEnv = ApigeeEnv.INTERNAL_DEV
    host: str = "https://api.enterprise.apigee.com"
    org: ApigeeOrg = ApigeeOrg.PROD

    def base_url(self):
        return f"{self.host}/v1/organizations/{self.org.value}"


@dataclass
class ApigeeApp:
    """ Data object to create an apigee app"""
    name: str
    attributes: List[dict] = field(default_factory=lambda: [{"name": "DisplayName", "value": "My App"}, ])
    apiProducts: List[str] = field(default_factory=lambda: ["identity-service-internal-dev"])
    callbackUrl: str = "www.example.com"
    scopes: List[str] = field(default_factory=lambda: [])
    status: str = "approved"

    def dict(self):
        return asdict(self)


class ApigeeService:
    def __init__(self, config: ApigeeConfig):
        self.base_url = config.base_url()
        self.default_headers = {}

        if username := config.username or os.getenv("APIGEE_USERNAME"):
            self.username = username
        else:
            raise ApigeeError("environment variable APIGEE_USERNAME is required")

        if access_token := config.access_token or apigee_access_token(self.username):
            self.default_headers["Authorization"] = f"Bearer {access_token}"
        else:
            raise ApigeeError("environment variable APIGEE_ACCESS_TOKEN is required")

    def get_applications(self):
        resource = f"developers/{self.username}/apps"
        url = f"{self.base_url}/{resource}"

        resp = requests.get(url=url, params={"email": self.username}, headers=self.default_headers)
        if resp.status_code != 200:
            raise ApigeeError(
                f"GET request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()

    def create_application(self, body: ApigeeApp):
        resource = f"developers/{self.username}/apps"
        url = f"{self.base_url}/{resource}"
        resp = requests.post(url=url, json=body.dict(), headers=self.default_headers)
        if resp.status_code != 201:
            raise ApigeeError(
                f"POST request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()

    def delete_application(self, name: str):
        resource = f"developers/{self.username}/apps/{name}"
        url = f"{self.base_url}/{resource}"
        resp = requests.delete(url=url, headers=self.default_headers)
        if resp.status_code != 200:
            raise ApigeeError(
                f"POST request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()
