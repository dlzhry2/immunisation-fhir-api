import requests
import uuid

from authentication import AppRestrictedAuth
from batch.errors import ImmunizationApiUnhandledError, ImmunizationApiError


class ImmunizationApi:
    def __init__(self, authenticator: AppRestrictedAuth, environment):
        self.authenticator = authenticator

        self.base_url = f"https://{environment}.api.service.nhs.uk/immunisation-fhir-api" \
            if environment != "prod" else "https://api.service.nhs.uk/immunisation-fhir-api"

    def create_immunization(self, immunization: dict, correlation_id: str):
        try:
            access_token = self.authenticator.get_access_token()
            request_headers = {
                'Authorization': f'Bearer {access_token}',
                'X-Request-ID': str(uuid.uuid4()),
                'X-Correlation-ID': correlation_id,
                "Content-Type": "application/fhir+json",
                "Accept": "application/fhir+json"
            }
            response = requests.post(f"{self.base_url}/Immunization",
                                     headers=request_headers,
                                     json=immunization,
                                     timeout=5)

            if response.status_code < 300:
                return response
            else:
                raise ImmunizationApiError(
                    request=immunization, response=response.json(),
                    status_code=response.status_code)

        except Exception as e:
            raise ImmunizationApiUnhandledError(request=immunization) from e
