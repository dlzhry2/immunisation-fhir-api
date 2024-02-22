import logging
import unittest

from factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path


class TestCreateImmunization(unittest.TestCase):
    apigee_service: ApigeeService
    product: ApigeeProduct
    app_restricted_app: ApigeeApp
    app_restricted_auth: AppRestrictedAuthentication

    base_url: get_service_base_path()
    app_token: str

    @classmethod
    def setUpClass(cls):
        display_name = f"test-{get_proxy_name()}"

        cls.apigee_service = make_apigee_service()
        cls.product = make_apigee_product(cls.apigee_service, display_name=display_name)
        cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service,
                                                                      display_name=display_name,
                                                                      product_name=cls.product.name)
        cls.app_restricted_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        try:
            cls.app_token = cls.app_restricted_auth.get_access_token()
        except Exception as e:
            logging.warning(e)
            pass

        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was created successfully"
                      f"and it was attached to the product {cls.product.name}: {cls.product}")

    @classmethod
    def tearDownClass(cls):
        cls.apigee_service.delete_application(cls.app_restricted_app.name)
        cls.apigee_service.delete_product(cls.product.name)
        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was deleted successfully")
        print(cls.app_token)
        print("yooooooo")

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
        # self.apigee_service.delete_application(self)
        # self.apigee_service.delete_application(self.app_restricted_app.name)
        # make_app_restricted_app()
