from time import time
from boto3 import resource
import requests
import json
import uuid


def lambda_handler(_event, _context):
    source_bucket_name = _event.get("Records")[0].get("s3").get("bucket").get("name")
    dest_bucket_name = source_bucket_name.replace("source", "destination")
    output_bucket = resource('s3').Bucket(dest_bucket_name)
    api_gateway_url = "https://hphlz3bvpb.execute-api.eu-west-2.amazonaws.com/alli5"

#getting JSON object
    s3_record = _event["Records"][0]["s3"]
    object_key = s3_record["object"]["key"]

#download JSON object from S3
    s3_object_url = f"s3://{source_bucket_name}/{object_key}"
    response = requests.get(s3_object_url)

#send JSON object to API-gateway if succesfully downloaded
    if response.status_code == 200:
        json_data = json.loads(response.text)
        filename = f"output_report_{time()}.txt"

# Send data to the API Gateway
        api_response = requests.post(api_gateway_url, json=payload_json)

#Construct JSON object to be sent to logged to output bucket
        payload = {
            "timestamp": f"output_report_{time()}.txt",
            "level": json_data,
            "request": {
                "x-request-id": str(uuid.uuid4()),
                "x-correlation-id": ""
            }
        }

#Convert payload to JSON string
        payload_json = json.dumps(payload)

#Send payload as JSON string to output bucket
        output_bucket.put_object(Body=json_data, Key=filename)

#return status codes depending on api_response
        if api_response.status_code == 200:
            return {
                'statusCode': 200,
                'body': 'Successfully sent JSON data to the API Gateway.'
            }
        else:
            return {
                'statusCode': api_response.status_code,
                'body': 'Error sending JSON data to the API Gateway.'
            }
    else:
        return {
            'statusCode': response.status_code,
            'body': 'Error fetching JSON object from S3.'
        }

# Write some placeholder bytestring data to a file in the bucket,
# so we can test that the lambda writes to the correct output bucket.
# filename = f"output_report_{time()}.txt"
# data = (b'Test file to see if the lambda writes to the correct s3 bucket. '
#         b'If our AWS bill skyrockets, this file has been written to the wrong bucket!')
# output_bucket.put_object(Body=data, Key=filename)
# return {
#     'statusCode': 200
# }