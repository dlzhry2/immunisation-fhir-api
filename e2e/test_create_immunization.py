import logging
import unittest

from factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from immunisation_api import ImmunisationApi
from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from resource_utils import create_an_imms_obj


class TestCreateImmunization(unittest.TestCase):
    apigee_service: ApigeeService
    product: ApigeeProduct
    app_restricted_app: ApigeeApp
    app_restricted_auth: AppRestrictedAuthentication

    imms_api: ImmunisationApi

    base_url: str
    app_token: str

    @classmethod
    def setUpClass(cls):
        display_name = f"test-{get_proxy_name()}"
        cls.base_url = get_service_base_path()

        cls.apigee_service = make_apigee_service()
        cls.product = make_apigee_product(cls.apigee_service, display_name=display_name)
        # cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service,
        #                                                               display_name=display_name,
        #                                                               product_name=cls.product.name)
        cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service)
        cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())
        cls.app_restricted_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        try:
            cls.app_token = cls.app_restricted_auth.get_access_token()
        except Exception as e:
            logging.warning(e)
            pass

        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was created successfully"
                      f"and it was attached to the product {cls.product.name}: {cls.product}")

        cls.imms_api = ImmunisationApi(cls.base_url, cls.app_token)
        print(cls.base_url)
        print(cls.app_token)

    @classmethod
    def tearDownClass(cls):
        # cls.apigee_service.delete_application(cls.app_restricted_app.name)
        # cls.apigee_service.delete_product(cls.product.name)
        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was deleted successfully")

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
        imms = create_an_imms_obj()

        result = self.imms_api.create_immunization(imms)

        print(result.text)
        self.assertEqual(result.status_code, 201)
        # self.assertEqual(result.text, "")
        # assert "Location" in result.headers
