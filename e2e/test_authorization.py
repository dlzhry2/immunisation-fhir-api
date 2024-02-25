import unittest
import uuid
from typing import Set

from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from utils.authorization import ApplicationRestrictedPermission as AppResPerm, make_permissions_attribute, \
    app_res_full_access
from utils.factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from utils.immunisation_api import ImmunisationApi
from utils.resource import create_an_imms_obj


class TestApplicationRestrictedAuthorization(unittest.TestCase):
    apigee_service: ApigeeService
    product: ApigeeProduct
    app: ApigeeApp
    imms_api: ImmunisationApi

    @classmethod
    def setUpClass(cls):
        cls.apigee_service = make_apigee_service()
        display_name = f"test-{get_proxy_name()}"

        product_data = ApigeeProduct(name=str(uuid.uuid4()),
                                     displayName=display_name,
                                     scopes=[f"urn:nhsd:apim:app:level3:immunisation-fhir-api"])
        cls.product = make_apigee_product(cls.apigee_service, product_data)
        cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())

        def make_app_data() -> ApigeeApp:
            _app = ApigeeApp(name=str(uuid.uuid4()))
            _app.set_display_name(display_name)
            _app.add_product(cls.product.name)
            return _app

        app_data = make_app_data()
        cls.app, app_res_cfg = make_app_restricted_app(cls.apigee_service, app_data)

        app_res_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        base_url = get_service_base_path()

        cls.imms_api = ImmunisationApi(base_url, app_res_auth)

    def setUp(self):
        # modify app to full access before each test so, we can arrange the test
        self.modify_permissions(set())

    @classmethod
    def tearDownClass(cls):
        cls.apigee_service.delete_application(cls.app.name)
        cls.apigee_service.delete_product(cls.product.name)

    def modify_permissions(self, permissions: Set[AppResPerm]):
        k, v = make_permissions_attribute(permissions)
        self.apigee_service.create_app_attribute(self.app.name, k, v)

    def test_create_imms_authorised(self):
        """it should create Immunization if app has immunization:create permission"""
        self.modify_permissions({AppResPerm.CREATE})

        imms = create_an_imms_obj()
        result = self.imms_api.create_immunization(imms)

        self.assertEqual(result.status_code, 201, result.text)

    def test_create_imms_unauthorised(self):
        """it should not create Immunization if app doesn't immunization:create permission"""
        perm = app_res_full_access(exclude={AppResPerm.CREATE})
        self.modify_permissions(perm)

        imms = create_an_imms_obj()
        result = self.imms_api.create_immunization(imms)

        self.assertEqual(result.status_code, 403, result.text)
