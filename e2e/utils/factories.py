import json
import os
import uuid

from lib.apigee import ApigeeService, ApigeeConfig, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedCredentials, AppRestrictedAuthentication, JwkKeyPair
from lib.env import get_apigee_access_token, get_auth_url, get_apigee_username, get_apigee_env, \
    get_default_app_restricted_credentials, get_proxy_name, upload_jwks_to_public_s3, get_public_bucket_name, \
    get_private_key_path

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


def make_apigee_product(apigee: ApigeeService = None, product: ApigeeProduct = None) -> ApigeeProduct:
    if not apigee:
        apigee = make_apigee_service()
    if not product:
        product = ApigeeProduct(name=str(uuid.uuid4()), scopes=[f"urn:nhsd:apim:app:level3:{get_proxy_name()}"])

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
        key_id = get_proxy_name()

        # jwks_pair = JwkKeyPair(key_id)
        jwks_pair = JwkKeyPair(key_id, private_key_path=get_private_key_path(),
                               public_key_path="/Users/jalal/projects/apim/immunisation-fhir-api/e2e/.keys/immunisation-fhir-api-local.key.pub")
        jwks_file_path = _write_jwks_files(jwks_pair)

        jwks_s3_key = f"{os.getenv('USER')}/{key_id}.json"
        jwks_url = upload_jwks_to_public_s3(bucket_name=get_public_bucket_name(), key=jwks_s3_key,
                                            file_path=jwks_file_path)

        app.add_attribute("jwks-resource-url", jwks_url)
        resp = apigee.create_application(app)
        stored_app = ApigeeApp.from_dict(resp)

        print(jwks_url)

        config = AppRestrictedCredentials(client_id=stored_app.get_client_id(),
                                          kid=key_id,
                                          private_key_content=jwks_pair.private_key)

        # sleep(10)
        return stored_app, config


def _write_jwks_files(pair: JwkKeyPair, jwks_path=JWKS_PATH) -> str:
    """Write jwks json file and also private key. It returns the path to jwks json file"""
    jwks_file = f"{jwks_path}/{pair.key_id}-with-new-pair.json"
    jwks = {"keys": [pair.make_jwk()]}
    os.makedirs(os.path.dirname(jwks_file), exist_ok=True)
    with open(jwks_file, "w+") as f:
        json.dump(jwks, f, indent=2)

    return jwks_file
