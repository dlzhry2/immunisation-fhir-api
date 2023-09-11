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


@pytest.mark.debug
@pytest.mark.smoketest
@pytest.mark.nhsd_apim_authorization(
        {
            "access": "healthcare_worker",
            "level": "aal3",
            "login_form": {"username": "656005750104"},
        }
    )
def test_lambda_crud(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    """
    Test for the POST,GET and Delete for Lambda endpoints.
    """
    timestamp = int(time.time())
    random.seed(timestamp)
    id = str(random.randint(0, 1000))
    expected_post_status_code = 201
    expected_delete_status_code = 200
    expected_get_status_code = 200
    headers = {
                "Content-Type": "application/json"
    }
    request_payload = {
                      "id": id,
                      "message": "Hello World"}
    json_payload = json.dumps(request_payload)

    headers.update(nhsd_apim_auth_headers)
    post_response = requests.post(
            url=f"{nhsd_apim_proxy_url}/event",
            headers=headers,
            data=json_payload
        )

    get_response = requests.get(
            url=f"{nhsd_apim_proxy_url}/event",
            headers=headers,
            params={
                "id": id
            }
        )

    delete_response = requests.delete(
            url=f"{nhsd_apim_proxy_url}/event",
            headers=headers,
            params={
                "id": id
            }
        )

    assert_that(expected_post_status_code).is_equal_to(post_response.status_code)
    assert_that(expected_delete_status_code).is_equal_to(delete_response.status_code)
    assert_that(expected_get_status_code).is_equal_to(get_response.status_code)
