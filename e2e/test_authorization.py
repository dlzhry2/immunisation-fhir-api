import logging
import unittest
import uuid
from typing import List

from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication, AuthType
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from utils.factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from utils.immunisation_api import ImmunisationApi
from utils.resource import create_an_imms_obj


class TestAuthorization(unittest.TestCase):
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
        cls.base_url = get_service_base_path()

        cls.apigee_service = make_apigee_service()
        # cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service,
        #                                                               display_name=display_name,
        #                                                               product_name=cls.product.name)
        display_name = f"test-{get_proxy_name()}"

        product = ApigeeProduct(name=str(uuid.uuid4()),
                                displayName=display_name,
                                scopes=[f"urn:nhsd:apim:app:level3:immunisation-fhir-api"])

        cls.product = make_apigee_product(cls.apigee_service, product)

        app = ApigeeApp(name=str(uuid.uuid4()))
        app.set_display_name(display_name)
        app.add_product(cls.product.name)
        cls.app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service, app)

        cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())

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
        cls.apigee_service.delete_application(cls.app_restricted_app.name)
        cls.apigee_service.delete_product(cls.product.name)
        logging.debug(f"app: {cls.app_restricted_app.name}: {cls.app_restricted_app.appId} was deleted successfully")

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
        # Given
        imms = create_an_imms_obj()

        # When
        result = self.app_res_imms_api.create_immunization(imms)

        # Then
        self.assertEqual(result.status_code, 201, result.text)
        self.assertEqual(result.text, "")
        self.assertTrue("Location" in result.headers)
