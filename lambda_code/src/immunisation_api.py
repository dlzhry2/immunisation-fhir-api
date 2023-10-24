import os
import http.client


class ImmunisationAPI:
    def __init__(self):
        self.api_gateway_url = os.getenv("SERVICE_DOMAIN_NAME")

    def post_event(self, payload_bytes_api_gateway, headers):
        connection = http.client.HTTPSConnection(self.api_gateway_url)
        connection.request("POST", "/", payload_bytes_api_gateway, headers=headers)
        response = connection.getresponse()
        print(response.status)
        connection.close()

        return response
