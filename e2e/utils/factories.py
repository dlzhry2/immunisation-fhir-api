import json
import os
import uuid

from lib.apigee import ApigeeService, ApigeeConfig, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedCredentials, AppRestrictedAuthentication, KeyManager, AuthType, JwkKeyPair
from lib.cache import Cache
from lib.env import get_apigee_access_token, get_auth_url, get_apigee_username, get_apigee_env, \
    get_default_app_restricted_credentials, get_proxy_name, upload_jwks_to_public_s3, get_public_bucket_name

JWKS_PATH = f"{os.getcwd()}/.well-known"
PRIVATE_KEY_PATH = f"{os.getcwd()}/.keys"


def make_apigee_service(config: ApigeeConfig = None) -> ApigeeService:
    config = config if config \
        else ApigeeConfig(username=get_apigee_username(), access_token=get_apigee_access_token(), env=get_apigee_env())
    return ApigeeService(config)


def make_app_restricted_auth(config: AppRestrictedCredentials = None) -> AppRestrictedAuthentication:
    """if config is None then we fall back to the default client configuration from env vars. Useful for Int env"""
    config = config if config else get_default_app_restricted_credentials()
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
                            app: ApigeeApp = None) -> (ApigeeApp, AppRestrictedCredentials):
    if not apigee:
        apigee = make_apigee_service()

    use_default_app = app is None
    if use_default_app:
        cred = get_default_app_restricted_credentials()
        stored_app = ApigeeApp(name="default-app")
        return stored_app, cred
    else:
        resp = apigee.create_application(app)
        stored_app = ApigeeApp.from_dict(resp)
        key_id = get_proxy_name()

        # jwks_pair = make_key_pair(key_id=key_id)
        jwks_pair = JwkKeyPair(key_id)
        jwks_file_path = _write_jwks_files(jwks_pair)

        jwks_s3_key = f"{os.getenv('USER')}/{key_id}.json"
        jwks_url = upload_jwks_to_public_s3(bucket_name=get_public_bucket_name(), key=jwks_s3_key,
                                            file_path=jwks_file_path)
        print(jwks_url)

        apigee.create_app_attribute(stored_app.name, "jwks-resource-url", jwks_url)

        config = AppRestrictedCredentials(client_id=stored_app.get_client_id(),
                                          kid=key_id,
                                          private_key_content=jwks_pair.private_key)

        return stored_app, config


def make_app_restricted_app4(apigee: ApigeeService = None,
                             name: str = str(uuid.uuid4()),
                             display_name: str = None,
                             product_name: str = None) -> (ApigeeApp, AppRestrictedCredentials):
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

    key_id = get_proxy_name()
    # jwks_pair = make_key_pair(key_id=key_id)
    jwks_pair = JwkKeyPair(key_id)
    jwks_file_path = _write_jwks_files(jwks_pair)

    jwks_s3_key = f"{os.getenv('USER')}/{key_id}.json"
    jwks_url = upload_jwks_to_public_s3(bucket_name=get_public_bucket_name(), key=jwks_s3_key,
                                        file_path=jwks_file_path)
    print(jwks_url)

    apigee.create_app_attribute(stored_app.name, "jwks-resource-url", jwks_url)

    config = AppRestrictedCredentials(client_id=stored_app.get_client_id(),
                                      kid=key_id,
                                      private_key_content=jwks_pair.private_key)

    return stored_app, config


def make_app_restricted_app3(apigee: ApigeeService = None,
                             name: str = str(uuid.uuid4()),
                             display_name: str = None,
                             product_name: str = None) -> (ApigeeApp, AppRestrictedCredentials):
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

    jwks_file = f"{os.getcwd()}/.well-known/{cache_id}-3.json"
    jwks = key_mgr.get_jwks(pub)
    os.makedirs(os.path.dirname(jwks_file), exist_ok=True)
    with open(jwks_file, "w+") as f:
        f.write(json.dumps(jwks))

    key_file = f"{os.getcwd()}/.keys/{cache_id}.pem"
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    with open(key_file, "w+") as f:
        f.write(prv.decode())

    pub_key = f"{os.getenv('USER')}/{cache_id}.json"
    pub_url = upload_jwks_to_public_s3(bucket_name=get_public_bucket_name(), key=pub_key, file_path=jwks_file)
    # pub_url = "https://immunization-fhir-api-public-key-host.s3.eu-west-2.amazonaws.com/jalal/immunisation-fhir-api-pr-100.json"
    apigee.create_app_attribute(stored_app.name, "jwks-resource-url", pub_url)

    # with open("/Users/jalal/projects/apim/immunisation-fhir-api/e2e/.keys/immunisation-fhir-api-pr-100.pem",
    #           "r") as prv:
    #     config = AppRestrictedConfig(client_id=stored_app.get_client_id(),
    #                                  kid=cache_id,
    #                                  private_key_content=prv.read())

    config = AppRestrictedCredentials(client_id=stored_app.get_client_id(),
                                      kid=cache_id,
                                      private_key_content=prv.decode())

    return stored_app, config


def _write_jwks_files(pair: JwkKeyPair, jwks_path=JWKS_PATH, private_key_path=PRIVATE_KEY_PATH) -> str:
    """Write jwks json file and also private key. It returns the path to jwks json file"""
    jwks_file = f"{jwks_path}/{pair.key_id}.json"
    jwks = {"keys": [pair.make_jwk()]}
    os.makedirs(os.path.dirname(jwks_file), exist_ok=True)
    with open(jwks_file, "w+") as f:
        json.dump(jwks, f, indent=2)

    # key_file = f"{private_key_path}/{pair.key_id}.pem"
    # os.makedirs(os.path.dirname(key_file), exist_ok=True)
    # with open(key_file, "w+") as f:
    #     f.write(pair.private_key)

    return jwks_file
