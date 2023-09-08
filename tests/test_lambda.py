"""
See
https://github.com/NHSDigital/pytest-nhsd-apim/blob/main/tests/test_examples.py
for more ideas on how to test the authorization of your API.
"""
import json
import random
import time
import pytest
import requests
from assertpy import assert_that


@pytest.mark.smoketest
@pytest.mark.debug
def test_lambda_crud(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """
    Test for the POST,GET and Delete for Lambda endpoints.
    """
    timestamp = int(time.time())
    random.seed(timestamp)
    id = random.randint(0, 1000)
    expected_post_status_code = 201
    expected_delete_status_code = 200
    expected_get_status_code = 200
    headers = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Content-Length": "59"
    }
    request_payload = {
                      "id": id,
                      "message": "Hello World"}
    json_payload = json.dumps(request_payload)
    post_response = requests.post(
            url=f"{nhsd_apim_proxy_url}/",
            headers=headers,
            data=json_payload
        )

    get_response = requests.get(
            url=f"{nhsd_apim_proxy_url}/",
            headers=headers,
            params={
                "id": id
            }
        )

    delete_response = requests.delete(
            url=f"{nhsd_apim_proxy_url}/id",
            headers=headers,
            params={
                "id": id
            }
        )

    assert_that(expected_post_status_code).is_equal_to(post_response.status_code)
    assert_that(expected_delete_status_code).is_equal_to(delete_response.status_code)
    assert_that(expected_get_status_code).is_equal_to(get_response.status_code)
