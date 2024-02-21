import json
import logging
import os
import unittest
import uuid

from lib.apigee import ApigeeService, ApigeeConfig, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedConfig, AppRestrictedAuthentication, KeyManager, AuthType
from lib.cache import Cache
from lib.env import get_apigee_access_token, get_auth_url, get_apigee_username, get_apigee_env, \
    get_default_app_restricted, get_proxy_name, upload_public_key_to_s3, get_public_bucket_name, get_service_base_path


def make_apigee_service(config: ApigeeConfig = None) -> ApigeeService:
    config = config if config \
        else ApigeeConfig(username=get_apigee_username(), access_token=get_apigee_access_token(), env=get_apigee_env())
    return ApigeeService(config)


def make_app_restricted_auth(config: AppRestrictedConfig = None) -> AppRestrictedAuthentication:
    """if config is None then we fall back to the default client configuration from env vars. Useful for Int env"""
    config = config if config else get_default_app_restricted()
    return AppRestrictedAuthentication(auth_url=get_auth_url(), config=config)


def make_apigee_product(apigee: ApigeeService = None,
                        name: str = str(uuid.uuid4()),
                        display_name: str = None) -> ApigeeProduct:
    if not apigee:
        apigee = make_apigee_service()
    product = ApigeeProduct(name=name, scopes=[f"urn:nhsd:apim:app:level3:{get_proxy_name()}"])
    if display_name:
        product.displayName = display_name

    resp = apigee.create_product(product)
    return ApigeeProduct.from_dict(resp)


def make_app_restricted_app(apigee: ApigeeService = None,
                            name: str = str(uuid.uuid4()),
                            display_name: str = None,
                            product_name: str = None) -> (ApigeeApp, AppRestrictedConfig):
    if not apigee:
        apigee = make_apigee_service()

    app = ApigeeApp(name=name, apiProducts=[product_name])
    if display_name:
        app.set_display_name(display_name)
    app.add_attribute("AuthenticationType", AuthType.APP_RESTRICTED.value)
    app.add_attribute("jwks-resource-url", "")
    app.add_attribute("environment", "dev")

    resp = apigee.create_application(app)
    stored_app = ApigeeApp.from_dict(resp)

    apigee.add_proxy_to_product(product_name=product_name, proxy_name=get_proxy_name())

    cache_id = f"{get_proxy_name()}"
    cache = Cache(cache_id=cache_id)

    key_mgr = KeyManager(key_id=cache_id, cache=cache)
    (prv, pub) = key_mgr.gen_private_public_pem()

    jwks_file = f"{os.getcwd()}/.well-known/{cache_id}.json"
    jwks = key_mgr.get_jwks(pub)
    os.makedirs(os.path.dirname(jwks_file), exist_ok=True)
    with open(jwks_file, "w+") as f:
        f.write(json.dumps(jwks))

    key_file = f"{os.getcwd()}/.keys/{cache_id}.pem"
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    with open(key_file, "w+") as f:
        f.write(prv.decode())

    pub_key = f"{os.getenv('USER')}/{cache_id}.json"
    pub_url = upload_public_key_to_s3(bucket_name=get_public_bucket_name(), key=pub_key, file_path=jwks_file)
    apigee.create_app_attribute(stored_app.name, "jwks-resource-url", pub_url)

    config = AppRestrictedConfig(client_id=stored_app.get_client_id(),
                                 kid=cache_id,
                                 private_key_content=prv.decode())

    return stored_app, config


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
        cls.app_token = cls.app_restricted_auth.get_access_token()

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
