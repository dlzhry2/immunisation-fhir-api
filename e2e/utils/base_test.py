import unittest
import uuid
import boto3
from typing import List
from botocore.config import Config
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from lib.apigee import ApigeeService, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedAuthentication
from lib.env import get_auth_url, get_proxy_name, get_service_base_path, get_imms_delta_table_name
from utils.factories import make_apigee_service, make_app_restricted_app, make_apigee_product
from utils.immunisation_api import ImmunisationApi, parse_location
from utils.resource import create_an_imms_obj


class ImmunizationBaseTest(unittest.TestCase):
    """It provides a set of apps with for each AuthType with full permission"""
    apigee_service: ApigeeService
    product: ApigeeProduct

    # a list of ImmunizationApi for each authentication type
    imms_apis: List[ImmunisationApi]
    # a list of all apps that was created, so we can delete them at the end
    apps: List[ApigeeApp]
    # an ImmunisationApi with default auth-type: ApplicationRestricted
    default_imms_api: ImmunisationApi
    imms_delta_table: Table

    @classmethod
    def setUpClass(cls):
        cls.apigee_service = make_apigee_service()
        display_name = f"test-{get_proxy_name()}"

        product_data = ApigeeProduct(name=str(uuid.uuid4()),
                                     displayName=display_name,
                                     # we only use one single product for all auth types
                                     # TODO(Cis2_AMB-1733) add scopes for Cis2
                                     # TODO(NhsLogin_AMB-1923) add scopes for NhsLogin
                                     scopes=["urn:nhsd:apim:app:level3:immunisation-fhir-api"])
        cls.product = make_apigee_product(cls.apigee_service, product_data)
        cls.apigee_service.add_proxy_to_product(product_name=cls.product.name, proxy_name=get_proxy_name())

        cls.apps = []
        cls.imms_apis = []

        def make_app_data() -> ApigeeApp:
            _app = ApigeeApp(name=str(uuid.uuid4()))
            _app.set_display_name(display_name)
            _app.add_product(cls.product.name)
            return _app

        def get_delta_table(region_name="eu-west-2") -> Table:
            config = Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1})
            db: DynamoDBServiceResource = boto3.resource(
                "dynamodb", region_name=region_name, config=config
            )
            return db.Table(get_imms_delta_table_name())
        # ApplicationRestricted
        app_data = make_app_data()
        app_restricted_app, app_res_cfg = make_app_restricted_app(cls.apigee_service, app_data)
        cls.apps.append(app_restricted_app)
        app_res_auth = AppRestrictedAuthentication(get_auth_url(), app_res_cfg)
        base_url = get_service_base_path()

        cls.default_imms_api = ImmunisationApi(base_url, app_res_auth)
        cls.imms_apis.append(cls.default_imms_api)
        cls.imms_delta_table = get_delta_table()

        # Cis2
        # TODO(Cis2_AMB-1733) create an app for Cis2 and append it to the cls.apps,
        #  then create ImmunisationApi and append it to cls.imms_apis

        # NhsLogin
        # TODO(NhsLogin_AMB-1923) create an app for NhsLogin and append it to the cls.apps,
        #  then create ImmunisationApi and append it to cls.imms_apis

    @classmethod
    def tearDownClass(cls):
        for app in cls.apps:
            cls.apigee_service.delete_application(app.name)
        cls.apigee_service.delete_product(cls.product.name)

    @staticmethod
    def create_immunization_resource(imms_api: ImmunisationApi, resource: dict = None) -> str:
        """creates an Immunization resource and returns the resource url"""
        imms = resource if resource else create_an_imms_obj()
        response = imms_api.create_immunization(imms)
        assert response.status_code == 201, response.text
        return parse_location(response.headers["Location"])

    @staticmethod
    def create_a_deleted_immunization_resource(imms_api: ImmunisationApi, resource: dict = None) -> dict:
        """it creates a new Immunization and then delete it, it returns the created imms"""
        imms = resource if resource else create_an_imms_obj()
        response = imms_api.create_immunization(imms)
        assert response.status_code == 201, response.text
        imms_id = parse_location(response.headers["Location"])
        response = imms_api.delete_immunization(imms_id)
        assert response.status_code == 204, response.text

        return imms

    def assert_operation_outcome(self, response, status_code: int, contains: str = ""):
        body = response.json()
        self.assertEqual(response.status_code, status_code, response.text)
        self.assertEqual(body["resourceType"], "OperationOutcome")
        self.assertTrue(contains in body["issue"][0]["diagnostics"])
