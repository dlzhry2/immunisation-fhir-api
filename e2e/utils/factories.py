import os
import os
import uuid
from typing import Set

from lib.apigee import ApigeeService, ApigeeConfig, ApigeeApp, ApigeeProduct
from lib.authentication import AppRestrictedCredentials, AppRestrictedAuthentication, AuthType
from lib.env import get_apigee_access_token, get_auth_url, get_apigee_username, get_apigee_env, \
    get_default_app_restricted_credentials, get_proxy_name
from lib.jwks import JwksData
from utils.authorization import ApplicationRestrictedPermission as AppResPerms, app_res_full_access, \
    make_permissions_attribute

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
                            app: ApigeeApp = None,
                            permissions: Set[AppResPerms] = None) -> (ApigeeApp, AppRestrictedCredentials):
    if not apigee:
        apigee = make_apigee_service()

    use_default_app = app is None
    if use_default_app:
        cred = get_default_app_restricted_credentials()
        stored_app = ApigeeApp(name="default-app")
        return stored_app, cred
    else:
        # we use this prefix for file names. This way we don't create a separate file for each jwks
        key_id_prefix = get_proxy_name()
        # NOTE: adding uuid is important. identity-service caches the key_id so,
        #  this way we know it'll be invalidated each time we create a new jwks
        key_id = f"{key_id_prefix}-{str(uuid.uuid4())}"

        jwks_data = JwksData(key_id)
        jwks_url = jwks_data.get_jwks_url(base_url="https://api.service.nhs.uk/mock-jwks")
        app.add_attribute("jwks-resource-url", jwks_url)

        if permissions := permissions or app_res_full_access():
            k, v = make_permissions_attribute(permissions)
            app.add_attribute(k, v)
        app.add_attribute("AuthenticationType", AuthType.APP_RESTRICTED.value)

        resp = apigee.create_application(app)
        stored_app = ApigeeApp.from_dict(resp)

        credentials = AppRestrictedCredentials(client_id=stored_app.get_client_id(),
                                               kid=key_id,
                                               private_key_content=jwks_data.private_key)

        return stored_app, credentials
