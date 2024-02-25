import uuid
from time import sleep
from typing import Set

from lib.apigee import ApigeeApp
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path
from test_search_immunization import mmr_code
from utils.authorization import ApplicationRestrictedPermission as AppResPerm, make_permissions_attribute, \
    app_res_full_access
from utils.base_test import ImmunizationBaseTest
from utils.constants import valid_nhs_number1
from utils.factories import make_app_restricted_app
from utils.immunisation_api import ImmunisationApi
from utils.resource import create_an_imms_obj


class TestApplicationRestrictedAuthorization(ImmunizationBaseTest):
    my_app: ApigeeApp
    my_imms_api: ImmunisationApi

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # calling super setUpClass gives us everything we need which, is useful for test setup
        #  however, we need to create a new app so, we can modify its permissions
        #  this new app and its api are called my_app and my_imms_api, i.e. app under test
        display_name = f"test-{get_proxy_name()}"

        def make_app_data() -> ApigeeApp:
            _app = ApigeeApp(name=str(uuid.uuid4()))
            _app.set_display_name(display_name)
            _app.add_product(cls.product.name)
            return _app

        app_data = make_app_data()
        cls.my_app, app_res_cfg = make_app_restricted_app(cls.apigee_service, app_data)

        app_res_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        base_url = get_service_base_path()

        cls.my_imms_api = ImmunisationApi(base_url, app_res_auth)

    @classmethod
    def tearDownClass(cls):
        cls.apigee_service.delete_application(cls.my_app.name)
        super().tearDownClass()

    def setUp(self):
        # modify app to zero access before each test
        self.modify_permissions(set())
        # NOTE: modifying attributes takes time and if it's not ready app uses old values
        sleep(2)

    def modify_permissions(self, permissions: Set[AppResPerm]):
        k, v = make_permissions_attribute(permissions)
        self.apigee_service.create_app_attribute(self.my_app.name, k, v)

    def test_get_imms_authorised(self):
        """it should get Immunization if app has immunization:read permission"""
        imms_id = self.create_immunization_resource(self.default_imms_api)
        self.modify_permissions({AppResPerm.READ})
        # When
        response = self.my_imms_api.get_immunization_by_id(imms_id)
        # Then
        self.assertEqual(response.status_code, 200, response.text)

    def test_get_imms_unauthorised(self):
        """it should not get Immunization if app doesn't have immunization:read permission"""
        # imms_id = self.create_immunization_resource(self.default_imms_api)

        perm = app_res_full_access(exclude={AppResPerm.READ})
        self.modify_permissions(perm)
        # When
        response = self.my_imms_api.get_immunization_by_id("id-doesn't-matter")
        # Then
        self.assertEqual(response.status_code, 403, response.text)

    def test_create_imms_authorised(self):
        """it should create Immunization if app has immunization:create permission"""
        self.modify_permissions({AppResPerm.CREATE})
        # When
        imms = create_an_imms_obj()
        response = self.my_imms_api.create_immunization(imms)
        # Then
        self.assertEqual(response.status_code, 201, response.text)

    def test_create_imms_unauthorised(self):
        """it should not create Immunization if app doesn't immunization:create permission"""
        perm = app_res_full_access(exclude={AppResPerm.CREATE})
        self.modify_permissions(perm)
        # When
        imms = create_an_imms_obj()
        result = self.my_imms_api.create_immunization(imms)
        # Then
        self.assertEqual(result.status_code, 403, result.text)

    def test_update_imms_authorised(self):
        """it should update Immunization if app has immunization:update and immunization:create permission"""
        imms = create_an_imms_obj()
        imms_id = self.create_immunization_resource(self.default_imms_api, imms)
        imms["id"] = imms_id

        self.modify_permissions({AppResPerm.CREATE, AppResPerm.UPDATE})
        # When
        response = self.my_imms_api.update_immunization(imms_id, imms)
        # Then
        self.assertEqual(response.status_code, 200, response.text)

    def test_update_imms_unauthorised(self):
        """it should not update Immunization if app doesn't immunization:update permission"""
        # imms = create_an_imms_obj()
        # imms_id = self.create_immunization_resource(self.default_imms_api, imms)
        # imms["id"] = imms_id

        perm = app_res_full_access(exclude={AppResPerm.UPDATE})
        self.modify_permissions(perm)
        # When
        response = self.my_imms_api.update_immunization("doesn't-matter", {})
        # Then
        self.assertEqual(response.status_code, 403, response.text)

    def test_update_imms_unauthorised_2(self):
        """it should not update Immunization if app doesn't immunization:create permission"""
        imms = create_an_imms_obj()
        imms_id = self.create_immunization_resource(self.default_imms_api, imms)
        imms["id"] = imms_id

        perm = app_res_full_access(exclude={AppResPerm.CREATE})
        self.modify_permissions(perm)
        # When
        response = self.my_imms_api.update_immunization(imms_id, imms)
        # Then
        self.assertEqual(response.status_code, 403, response.text)

    def test_delete_imms_authorised(self):
        """it should delete Immunization if app has immunization:delete permission"""
        imms_id = self.create_immunization_resource(self.default_imms_api)
        self.modify_permissions({AppResPerm.DELETE})
        # When
        response = self.my_imms_api.delete_immunization(imms_id)
        # Then
        self.assertEqual(response.status_code, 204, response.text)

    def test_delete_imms_unauthorised(self):
        """it should not delete Immunization if app doesn't have immunization:delete permission"""
        # imms_id = self.create_immunization_resource(self.default_imms_api)

        perm = app_res_full_access(exclude={AppResPerm.DELETE})
        self.modify_permissions(perm)
        # When
        response = self.my_imms_api.delete_immunization("doesn't-matter")
        # Then
        self.assertEqual(response.status_code, 403, response.text)

    def test_search_imms_authorised(self):
        """it should search Immunization if app has immunization:search permission"""
        mmr = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        _ = self.create_immunization_resource(self.default_imms_api, mmr)

        self.modify_permissions({AppResPerm.SEARCH})
        # When
        response = self.my_imms_api.search_immunizations(valid_nhs_number1, "MMR")
        # Then
        self.assertEqual(response.status_code, 200, response.text)

    def test_search_imms_unauthorised(self):
        """it should not search Immunization if app doesn't immunization:search permission"""
        # mmr = create_an_imms_obj(str(uuid.uuid4()), valid_nhs_number1, mmr_code)
        # _ = self.create_immunization_resource(self.default_imms_api, mmr)
        #
        perm = app_res_full_access(exclude={AppResPerm.SEARCH})
        self.modify_permissions(perm)
        # When
        response = self.my_imms_api.search_immunizations(valid_nhs_number1, "MMR")
        # Then
        self.assertEqual(response.status_code, 403, response.text)
