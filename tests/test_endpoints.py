"""
See
https://github.com/NHSDigital/pytest-nhsd-apim/blob/main/tests/test_examples.py
for more ideas on how to test the authorization of your API.
"""
from os import getenv

import pytest
import requests


@pytest.fixture()
def proxy_url():
    base_path = getenv("SERVICE_BASE_PATH")
    apigee_env = getenv("APIGEE_ENVIRONMENT")

    return f"https://{apigee_env}.api.service.nhs.uk/{base_path}"


@pytest.mark.smoketest
def test_ping(proxy_url):
    resp = requests.get(f"{proxy_url}/_ping")
    assert resp.status_code == 200


@pytest.mark.smoketest
def test_wait_for_ping(proxy_url):
    retries = 0
    resp = requests.get(f"{proxy_url}/_ping")
    deployed_commitId = resp.json().get("commitId")

    while (deployed_commitId != getenv('SOURCE_COMMIT_ID')
            and retries <= 30
            and resp.status_code == 200):
        resp = requests.get(f"{proxy_url}/_ping")
        deployed_commitId = resp.json().get("commitId")
        retries += 1

    if resp.status_code != 200:
        pytest.fail(f"Status code {resp.status_code}, expecting 200")
    elif retries >= 30:
        pytest.fail("Timeout Error - max retries")

    assert deployed_commitId == getenv('SOURCE_COMMIT_ID')


@pytest.mark.smoketest
def test_status(proxy_url):
    resp = requests.get(
        f"{proxy_url}/_status", headers={"apikey": getenv("STATUS_ENDPOINT_API_KEY")}
    )
    assert resp.status_code == 200


@pytest.mark.smoketest
def test_wait_for_status(proxy_url):
    retries = 0
    resp = requests.get(f"{proxy_url}/_status", headers={"apikey": getenv("STATUS_ENDPOINT_API_KEY")})
    deployed_commitId = resp.json().get("commitId")

    while (deployed_commitId != getenv('SOURCE_COMMIT_ID')
            and retries <= 30
            and resp.status_code == 200
            and resp.json().get("version")):
        resp = requests.get(f"{proxy_url}/_status", headers={"apikey": getenv("STATUS_ENDPOINT_API_KEY")})
        deployed_commitId = resp.json().get("commitId")
        retries += 1

    if resp.status_code != 200:
        pytest.fail(f"Status code {resp.status_code}, expecting 200")
    elif retries >= 30:
        pytest.fail("Timeout Error - max retries")
    elif not resp.json().get("version"):
        pytest.fail("version not found")

    assert deployed_commitId == getenv('SOURCE_COMMIT_ID')


@pytest.mark.nhsd_apim_authorization({"access": "application", "level": "level0"})
def test_app_level0(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    resp = requests.get(f"{nhsd_apim_proxy_url}/event", headers=nhsd_apim_auth_headers)
    assert resp.status_code == 401  # unauthorized


@pytest.mark.nhsd_apim_authorization({"access": "application", "level": "level0"})
def test_aws_service_not_running_without_cert(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    service_domain_name = getenv('AWS_DOMAIN_NAME')
    with pytest.raises(requests.exceptions.RequestException) as excinfo:
        requests.get(f"{service_domain_name}/status", headers=nhsd_apim_auth_headers)
    assert "ConnectionResetError" in str(excinfo.value)
