import http.client
import os


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


class S3Service:

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def get_key_data(self, key):
        return {"patient": 123}

    def write_report(self, report):
        pass
