import os
from dataclasses import dataclass
from enum import Enum

import requests

import env


class ApigeeOrg(str, Enum):
    PROD = "nhsd-prod"
    NON_PROD = "nhsd-nonprod"


@dataclass
class ApigeeError(RuntimeError):
    message: str


@dataclass
class ApigeeConfig:
    username: str = None
    access_token: str = None
    host: str = "https://api.enterprise.apigee.com"
    org: ApigeeOrg = ApigeeOrg.PROD

    def base_url(self):
        return f"{self.host}/v1/organizations/{self.org.value}"


class ApigeeService:
    def __init__(self, config: ApigeeConfig):
        self.base_url = config.base_url()

        if username := config.username or os.getenv("APIGEE_USERNAME"):
            self.username = username
        else:
            raise ApigeeError("environment variable APIGEE_USERNAME is required")

        if access_token := config.access_token or env.apigee_access_token():
            self.access_token = access_token
        else:
            raise ApigeeError("environment variable APIGEE_ACCESS_TOKEN is required")

    def get_applications(self):
        resource = f"/developers/{self.username}/apps"
        url = f"{self.base_url}{resource}"

        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.get(url=url, params={"email": self.username}, headers=headers)
        if resp.status_code != 200:
            raise ApigeeError(
                f"GET request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()
