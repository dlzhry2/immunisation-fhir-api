import os

import requests


class ImmunisationApi:
    def __init__(self):
        self.api_gateway_url = os.getenv("SERVICE_DOMAIN_NAME")

    def post_event(self, payload_bytes_api_gateway, headers):
        response = requests.get('http://twitter.com/api/1/foobar')

        return response


class S3Service:

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def get_source_data(self, key):
        return {"patient": 123}

    def write_error_report(self, key):
        return {"patient": 123}

    # todo: remove this
    def get_key_data(self, key):
        return {"patient": 123}

    # todo: remove this
    def write_report(self, report):
        pass
