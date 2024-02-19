from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

import requests


class ApigeeOrg(str, Enum):
    PROD = "nhsd-prod"
    NON_PROD = "nhsd-nonprod"


class ApigeeEnv(str, Enum):
    INTERNAL_DEV = "internal-dev"
    SANDBOX = "sandbox"
    INT = "int"
    PROD = "prod"


@dataclass
class ApigeeError(RuntimeError):
    message: str


@dataclass
class ApigeeConfig:
    username: str
    access_token: str
    env: ApigeeEnv = ApigeeEnv.INTERNAL_DEV
    host: str = "https://api.enterprise.apigee.com"
    org: ApigeeOrg = ApigeeOrg.NON_PROD

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


@dataclass
class ApigeeProduct:
    """Data object to create an apigee product"""
    name: str
    apiResources: List[str] = field(default_factory=lambda: ["/"])
    approvalType: str = "auto"
    attributes: List[dict] = field(default_factory=lambda: [])
    description: str = "My API product"
    displayName: str = "My API product"
    environments: List[str] = field(default_factory=lambda: [ApigeeEnv.INTERNAL_DEV.value])
    proxies: List[str] = field(default_factory=lambda: ["identity-service-internal-dev"])
    scopes: List[str] = field(default_factory=lambda: [])

    def dict(self):
        return asdict(self)


class ApigeeService:
    def __init__(self, config: ApigeeConfig):
        self.base_url = config.base_url()
        self.username = config.username
        self.default_headers = {"Authorization": f"Bearer {config.access_token}"}

    def get_applications(self) -> dict:
        params = {"email": self.username}
        resource = f"developers/{self.username}/apps"
        return self._get(resource, params)

    def create_application(self, app: ApigeeApp) -> dict:
        resource = f"developers/{self.username}/apps"
        return self._create(resource, app.dict())

    def delete_application(self, name: str) -> dict:
        resource = f"developers/{self.username}/apps/{name}"
        return self._delete(resource)

    def get_app_attribute(self, app_name: str, attr_name: str) -> dict:
        resource = f"/developers/{self.username}/apps/{app_name}/attributes/{attr_name}"
        return self._get(resource, {})

    def create_app_attribute(self, app_name: str, attr_name: str, body: dict) -> dict:
        resource = f"/developers/{self.username}/apps/{app_name}/attributes/{attr_name}"
        return self._create(resource, body)

    def delete_app_attribute(self, app_name: str, attr_name: str) -> dict:
        resource = f"/developers/{self.username}/apps/{app_name}/attributes/{attr_name}"
        return self._delete(resource)

    def create_product(self, product: ApigeeProduct) -> dict:
        resource = "apiproducts"
        return self._create(resource, product.dict())

    def delete_product(self, name: str):
        resource = f"apiproducts/{name}"
        return self._delete(resource)

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}/{path}"
        resp = requests.get(url=url, params=params, headers=self.default_headers)
        if resp.status_code != 200:
            raise ApigeeError(
                f"GET request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()

    def _create(self, path: str, body: dict) -> dict:
        url = f"{self.base_url}/{path}"
        resp = requests.post(url=url, json=body, headers=self.default_headers)
        if resp.status_code != 201:
            raise ApigeeError(
                f"POST request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()

    def _delete(self, path: str) -> dict:
        url = f"{self.base_url}/{path}"
        resp = requests.delete(url=url, headers=self.default_headers)
        if resp.status_code != 200:
            raise ApigeeError(
                f"DELETE request to {resp.url} failed with status_code: {resp.status_code}, "
                f"Reason: {resp.reason} and Content: {resp.text}")
        return resp.json()
