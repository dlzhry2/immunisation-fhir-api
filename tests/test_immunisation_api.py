import pytest


class ImmunisationApi:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def get_event_by_id(self, event_id):
        # Make your request to our api here and return the response
        return "response"


# TODO: send a GET /event/{id} request
# This should give you 404 not found, since there is no event yet (we don't have POST)
# Test happy test manually. In both scenarios make sure lambda is getting executed
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_get_event_by_id_not_found_nhs_login(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # token = nhsd_apim_auth_headers["access_token"]  # <- not tested
    token = "token"
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    res = imms_api.get_event_by_id("some-id-that-does-not-exist")
    print(res)
    # Make assertions


@pytest.mark.smoketest
@pytest.mark.nhsd_apim_authorization(
    {
        "access": "application",
        "level": "level3"
    })
def test_get_event_by_id_not_found_app_restricted(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    # TODO same here but with app restricted, probably refactor both into a function instead of copy paste
    # token = nhsd_apim_auth_headers["access_token"]  # <- not tested
    token = "token"
    imms_api = ImmunisationApi(nhsd_apim_proxy_url, token)
    res = imms_api.get_event_by_id("some-id-that-does-not-exist")
    print(res)
    # Make assertions
