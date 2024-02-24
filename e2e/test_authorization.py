import unittest
import uuid
from typing import List

from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from utils.factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from utils.immunisation_api import ImmunisationApi
from utils.resource import create_an_imms_obj


class TestAuthorization(unittest.TestCase):
    apigee_service: ApigeeService
    product: ApigeeProduct

    # a list of ImmunizationApi for each authentication type
    imms_apis: List[ImmunisationApi]
    # a list of all apps that was created, so we can delete them at the end
    apps: List[ApigeeApp]
    # an ImmunisationApi with default auth-type: ApplicationRestricted
    default_imms_api: ImmunisationApi

    @classmethod
    def setUpClass(cls):
        cls.apigee_service = make_apigee_service()
        display_name = f"test-{get_proxy_name()}"

        product_data = ApigeeProduct(name=str(uuid.uuid4()),
                                     displayName=display_name,
                                     # we only use one single product for all auth types
                                     # TODO(Cis2): add scopes for Cis2
                                     # TODO(NhsLogin): add scopes for NhsLogin
                                     scopes=[f"urn:nhsd:apim:app:level3:immunisation-fhir-api"])
        cls.product = make_apigee_product(cls.apigee_service, product_data)
        cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())

        cls.apps = []
        cls.imms_apis = []

        def make_app_data() -> ApigeeApp:
            _app = ApigeeApp(name=str(uuid.uuid4()))
            _app.set_display_name(display_name)
            _app.add_product(cls.product.name)
            return _app

        # ApplicationRestricted
        app_data = make_app_data()
        app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service, app_data)
        cls.apps.append(app_restricted_app)

        app_res_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        base_url = get_service_base_path()

        cls.default_imms_api = ImmunisationApi(base_url, app_res_auth)
        cls.imms_apis.append(cls.default_imms_api)

        # Cis2
        # TODO(Cis2) create an app for Cis2 and append it to the cls.apps,
        #  then create ImmunisationApi and append it to cls.imms_apis

        # NhsLogin
        # TODO(NhsLogin) create an app for NhsLogin and append it to the cls.apps,
        #  then create ImmunisationApi and append it to cls.imms_apis

    @classmethod
    def tearDownClass(cls):
        for app in cls.apps:
            cls.apigee_service.delete_application(app.name)
        cls.apigee_service.delete_product(cls.product.name)

    def test_create_imms(self):
        """it should create a FHIR Immunization resource"""
        # Given
        imms = create_an_imms_obj()

        # When
        result = self.default_imms_api.create_immunization(imms)

        # Then
        self.assertEqual(result.status_code, 201, result.text)
        self.assertEqual(result.text, "")
        self.assertTrue("Location" in result.headers)
