import logging
import os
import subprocess

from .apigee import ApigeeEnv
from .authentication import AppRestrictedConfig
from .cache import Cache

"""use functions in this module to get configs that can be read from environment variables or external processes"""


def get_apigee_username():
    if username := os.getenv("APIGEE_USERNAME"):
        return username
    else:
        logging.error('environment variable "APIGEE_USERNAME" is required')


def get_apigee_env() -> ApigeeEnv:
    if env := os.getenv("APIGEE_ENVIRONMENT"):
        try:
            return ApigeeEnv(env)
        except ValueError:
            logging.error(f'the environment variable "APIGEE_ENVIRONMENT: {env}" is invalid')
    else:
        logging.warning('the environment variable "APIGEE_ENVIRONMENT" is empty, '
                        'falling back to the default value: "internal-dev"')
        return ApigeeEnv.INTERNAL_DEV


def get_apigee_access_token(username: str = None):
    if access_token := os.getenv("APIGEE_ACCESS_TOKEN"):
        return access_token

    if username := username or get_apigee_username():
        env = os.environ.copy()
        env["SSO_LOGIN_URL"] = env.get("SSO_LOGIN_URL", "https://login.apigee.com")
        try:
            res = subprocess.run(["get_token", "-u", username], env=env, stdout=subprocess.PIPE, text=True)
            return res.stdout.strip()
        except FileNotFoundError:
            logging.error("Make sure you install apigee's get_token utility and make sure it's in your PATH. "
                          "Follow: https://docs.apigee.com/api-platform/system-administration/using-gettoken")


def get_default_app_restricted() -> AppRestrictedConfig:
    client_id = os.getenv("DEFAULT_CLIENT_ID")
    kid = os.getenv("DEFAULT_KID")
    if not client_id or not kid:
        logging.error('Both "DEFAULT_CLIENT_ID" and "DEFAULT_KID" are required')
    private_key = get_private_key()

    return AppRestrictedConfig(client_id=client_id, kid=kid, private_key_content=private_key)


def get_private_key(file_path: str = None) -> str:
    if file_path := file_path or os.getenv("APP_RESTRICTED_PRIVATE_KEY_PATH"):
        with open(file_path, "r") as f:
            return f.read()
    else:
        raise RuntimeError('APP_RESTRICTED_PRIVATE_KEY_PATH is required. It should be the absolute path to your '
                           'application-restricted private-key')


def get_auth_url(apigee_env: ApigeeEnv = None) -> str:
    if not apigee_env:
        apigee_env = get_apigee_env()

    if apigee_env == ApigeeEnv.PROD:
        return "https://api.service.nhs.uk/oauth2"
    else:
        return f"https://{apigee_env.value}.api.service.nhs.uk/oauth2"


def get_proxy_name() -> str:
    if not os.getenv("PROXY_NAME"):
        raise RuntimeError('"PROXY_NAME" is required')
    return os.getenv("PROXY_NAME")


def get_service_base_path(apigee_env: ApigeeEnv = None) -> str:
    if not os.getenv("SERVICE_BASE_PATH"):
        raise RuntimeError('"SERVICE_BASE_PATH" is required')
    apigee_env = apigee_env if apigee_env else get_apigee_env()

    base_path = os.getenv("SERVICE_BASE_PATH")
    return f"https://{apigee_env.value}.api.service.nhs.uk/{base_path}"


def get_cache(cache_id: str = None) -> Cache:
    """We use a combination of the proxy name and USER for cache id by default.
    This way cache only expires when you open a new PR
    NOTE: choose a random value makes the cache to invalidate immediately. Useful for debugging
    """
    if cache_id := cache_id or f"{get_proxy_name()}_{os.getenv('USER')}":
        return Cache(cache_id=cache_id)


def get_public_bucket_name() -> str:
    if not os.getenv("PUBLIC_BUCKET_NAME"):
        raise RuntimeError('"PUBLIC_BUCKET_NAME" is required')
    return os.getenv("PUBLIC_BUCKET_NAME")


def upload_jwks_to_public_s3(bucket_name: str, key: str, file_path: str) -> str:
    """uploads jwks file to a s3 bucket and returns the public url to the object"""
    with open(file_path, "r") as jwks:
        content = jwks.readline().lower()
        if "private" in content:
            logging.error("DANGER: it appears you are trying to upload private key instead of public key.\n"
                          "DO NOT share your private key and do not upload it anywhere public")

    bucket_url = f"s3://{bucket_name}/{key}"
    cmd = ["aws", "s3", "cp", file_path, bucket_url]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if res.returncode != 0:
            cmd_str = " ".join(cmd)
            raise RuntimeError(f"Failed to run command: '{cmd_str}'\nDiagnostic: Try to run the same command in the "
                               f"same terminal. Make sure you are authenticated\n{res.stdout}")
    except FileNotFoundError:
        logging.error("Make sure you install aws cli and make sure it's in your PATH. "
                      "Follow: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
    except RuntimeError as e:
        raise RuntimeError(f"failed to upload file: {file_path} to the bucket {bucket_url}\n{e}")

    return f"https://{bucket_name}.s3.eu-west-2.amazonaws.com/{key}"


def main():
    # a = get_apigee_access_token("jalal.hosseini1@nhs.net")
    p = "/Users/jalal/projects/apim/immunisation-fhir-api/e2e/services/mykey.pem"
    bn = "immunization-fhir-api-public-key-host"
    upload_jwks_to_public_s3(bn, "jalal2", p)


if __name__ == '__main__':
    main()
