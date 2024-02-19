import unittest

from services.apigee import ApigeeService, ApigeeConfig, ApigeeApp
from services.authentication import AppRestrictedConfig, AppRestrictedAuthentication
from services.env import get_apigee_access_token, get_auth_url, get_apigee_username, get_apigee_env, \
    get_default_app_restricted


def make_apigee_service(config: ApigeeConfig = None) -> ApigeeService:
    config = config if config \
        else ApigeeConfig(username=get_apigee_username(), access_token=get_apigee_access_token(), env=get_apigee_env())
    return ApigeeService(config)


def make_app_restricted_auth(config: AppRestrictedConfig = None) -> AppRestrictedAuthentication:
    """if config is None then we fall back to the default client configuration from env vars. Useful for Int env"""
    config = config if config else get_default_app_restricted()
    return AppRestrictedAuthentication(auth_url=get_auth_url(), config=config)


def make_app_restricted_app(apigee: ApigeeService = None) -> ApigeeApp:
    if not apigee:
        apigee = make_apigee_service()
    pass


class TestCreateImmunization(unittest.TestCase):
    def setUpClass(cls):
        pass

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
