import requests


def create_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/fhir+json",
        },
        "body": body
    }


class ImmunisationApi:
    def __init__(self, url):
        self.url = url

    def post_event(self, payload):
        headers = {
            "Content-Type": "application/fhir+json",
        }
        endpoint = f"{self.url}/event"
        response = requests.post(url=endpoint, json=payload, headers=headers)

        return response
