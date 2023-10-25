import boto3
import requests


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


def get_s3_object(bucket, key):
    client = boto3.client("s3")
    resp = client.get_object(Bucket=bucket, Key=key)

    return resp["Body"].read().decode("utf-8")


def write_s3_object(bucket, key, content):
    client = boto3.client("s3")
    resp = client.put_object(Bucket=bucket, Key=key, Body=content)
    return resp


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
