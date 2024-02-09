import pytest


@pytest.mark.nhsd_apim_authorization(
    {
        "access": "healthcare_worker",
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }
)
def test_crud_create(nhsd_apim_proxy_url, nhsd_apim_auth_headers):
    pass
