"""
See
https://github.com/NHSDigital/pytest-nhsd-apim/blob/main/tests/test_examples.py
for more ideas on how to test the authorization of your API.
"""
import json
import random
import time
import os
import pytest
import requests
from assertpy import assert_that


@pytest.fixture()
def proxy_url():
    base_path = os.getenv("SERVICE_BASE_PATH")
    apigee_env = os.getenv("APIGEE_ENVIRONMENT")

    return f"https://{apigee_env}.api.service.nhs.uk/{base_path}"


@pytest.mark.smoketest
def test_lambda_crud(proxy_url):
    """
    Test for the POST,GET and Delete for Lambda endpoints.
    """
    timestamp = int(time.time())
    random.seed(timestamp)
    id = random.randint(0, 1000)
    expected_post_status_code = 201
    expected_delete_status_code = 200
    expected_get_status_code = 200
    request_payload = {
                      "id": id,
                      "message": "Hello World"}
    json_payload = json.dumps(request_payload)
    post_response = requests.post(
            url=f"{proxy_url}/",
            data=json_payload
        )

    get_response = requests.get(
            url=f"{proxy_url}/",
            params={
                "id": id
            }
        )

    delete_response = requests.delete(
            url=f"{proxy_url}/id",
            params={
                "id": id
            }
        )

    assert_that(expected_post_status_code).is_equal_to(post_response.status_code)
    assert_that(expected_delete_status_code).is_equal_to(delete_response.status_code)
    assert_that(expected_get_status_code).is_equal_to(get_response.status_code)
