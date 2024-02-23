import functools
import logging
import unittest
from typing import List

from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication, AuthType
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from utils.factories import make_apigee_service, make_app_restricted_app
from utils.immunisation_api import ImmunisationApi, parse_location
from utils.resource import create_an_imms_obj


class ImmunizationBaseTest(unittest.TestCase):
    """provides a set of utilities
    Do not use this for keeping the state like, token, etc
    """
    apigee_service: ApigeeService
    product: ApigeeProduct
    app_restricted_app: ApigeeApp
    app_restricted_auth: AppRestrictedAuthentication

    app_res_imms_api: ImmunisationApi
    """a list of ImmunizationApi for each authentication type"""
    imms_apis: List[ImmunisationApi]

    base_url: str
    app_token: str

    @classmethod
    def setUpClass(cls):
        display_name = f"test-{get_proxy_name()}"
        cls.base_url = get_service_base_path()

        cls.apigee_service = make_apigee_service()
        # cls.product = make_apigee_product(cls.apigee_service, display_name=display_name)
        # cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service,
        #                                                               display_name=display_name,
        #                                                               product_name=cls.product.name)
        cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service)
        # cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())
        cls.app_restricted_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        try:
            cls.app_token = cls.app_restricted_auth.get_access_token()
        except Exception as e:
            logging.warning(e)
            pass

        # logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was created successfully"
        #               f"and it was attached to the product {cls.product.name}: {cls.product}")

        cls.app_res_imms_api = ImmunisationApi(cls.base_url, cls.app_token, AuthType.APP_RESTRICTED)
        cls.imms_apis = [cls.app_res_imms_api]

    @classmethod
    def tearDownClass(cls):
        # cls.apigee_service.delete_application(cls.app_restricted_app.name)
        # cls.apigee_service.delete_product(cls.product.name)
        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was deleted successfully")

    @staticmethod
    def create_immunization_resource(imms_api: ImmunisationApi, resource: dict = None) -> str:
        """creates an Immunization resource and returns the resource url"""
        imms = resource if resource else create_an_imms_obj()
        result = imms_api.create_immunization(imms)
        assert result.status_code == 201
        return parse_location(result.headers["Location"])

    @staticmethod
    def create_a_deleted_immunization_resource(imms_api: ImmunisationApi, resource: dict = None) -> dict:
        """it creates a new Immunization and then delete it, it returns the created imms"""
        imms = resource if resource else create_an_imms_obj()
        response = imms_api.create_immunization(imms)
        assert response.status_code == 201
        imms_id = parse_location(response.headers["Location"])
        response = imms_api.delete_immunization(imms_id)
        assert response.status_code == 204

        return imms

    def assert_operation_outcome(self, response, status_code: int, contains: str = ""):
        body = response.json()
        self.assertEqual(response.status_code, status_code, response.text)
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertTrue(contains in body["issue"][0]["diagnostics"])


def sub_test(param_list):
    """Decorates a test case to run it as a set of subtests."""

    def decorator(f):
        @functools.wraps(f)
        def wrapped(self):
            for param in param_list:
                with self.subTest(**param):
                    f(self, **param)

        return wrapped

    return decorator
