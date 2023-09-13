from time import time
from boto3 import resource
import http.client
import json
import uuid


def lambda_handler(_event, _context):
    source_bucket_name = _event.get("Records")[0].get("s3").get("bucket").get("name")
    dest_bucket_name = source_bucket_name.replace("source", "destination")
    output_bucket = resource('s3').Bucket(dest_bucket_name)
    api_gateway_url = "https://hphlz3bvpb.execute-api.eu-west-2.amazonaws.com/alli5"

# getting JSON object
    s3_record = _event["Records"][0]["s3"]
    object_key = s3_record["object"]["key"]

# download JSON object from S3
    s3_object_url = f"s3://{source_bucket_name}/{object_key}"
    conn = http.client.HTTPSConnection(api_gateway_url)
    conn.request("GET", s3_object_url)
    
    response = conn.getresponse()

# send JSON object to API-gateway if successfully downloaded
    if response.status == 200:
        json_data = json.loads(response.read().decode('utf-8'))
        filename = f"output_report_{time()}.txt"

# Send data to the API Gateway
        payload = json.dumps(json_data)
        headers = {
            "Content-Type": "application/json"
        }
        conn.request("POST", "/alli5", body=payload, headers=headers)
        api_response = conn.getresponse()

# Construct JSON object to be sent to the output bucket
        request_id = str(uuid.uuid4())
        payload = {
            "timestamp": filename,
            "level": json_data,
            "request": {
                "x-request-id": request_id,
                "x-correlation-id": request_id
            }
        }

# Convert payload to JSON string
        payload_json = json.dumps(payload)

# Send payload as JSON string to output bucket
        output_bucket.put_object(Body=payload_json, Key="body")

# Return status codes depending on api_response
        if api_response.status == 200:
            return {
                'statusCode': 200,
                'body': 'Successfully sent JSON data to the API Gateway.'
            }
        else:
            return {
                'statusCode': api_response.status,
                'body': 'Error sending JSON data to the API Gateway.'
            }
    else:
        return {
            'statusCode': response.status,
            'body': 'Error fetching JSON object from S3.'
        }
