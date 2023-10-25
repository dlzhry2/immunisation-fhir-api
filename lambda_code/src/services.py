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


class S3Service:
    @staticmethod
    def get_s3_object(bucket, key):
        client = boto3.client("s3")
        resp = client.get_object(Bucket=bucket, Key=key)

        return resp["Body"].read().decode("utf-8")

    @staticmethod
    def write_s3_object(bucket, key, content):
        client = boto3.client("s3")
        resp = client.put_object(Bucket=bucket, Key=key, Body=content)
        return resp
