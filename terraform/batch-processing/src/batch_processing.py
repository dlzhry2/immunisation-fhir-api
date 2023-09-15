from time import time
from urllib import request
from boto3 import resource
import http.client
import json
import uuid
import os
import boto3


def lambda_handler(_event, _context):
    # Check if "Records" key exists and it's a non-empty list
    if "Records" in _event and isinstance(_event["Records"], list) and len(_event["Records"]) > 0:
        s3_record = _event["Records"][0]["s3"]
        array_path = _event.get("Records").get("key")
        
        # Check if "bucket" key exists and it's a dictionary
        if "bucket" in s3_record and isinstance(s3_record["bucket"], dict):
            source_bucket_name = s3_record["bucket"].get("name")

            # Check if "object" key exists and it's a dictionary
            if "object" in s3_record and isinstance(s3_record["object"], dict):
                dest_bucket_name = source_bucket_name.replace("source", "destination")
                output_bucket = resource('s3').Bucket(dest_bucket_name)
                api_gateway_url = os.getenv("SERVICE_DOMAIN_NAME")
                s3_client = boto3.client('s3')
                
                try:
                    # Get the array of objects from the S3 bucket
                    response = s3_client.get_object(Bucket=source_bucket_name, Key=array_path)
                    
                    # Read the object's content
                    object_content = response['Body'].read().decode('utf-8')
                    
                    # Parse the JSON content
                    data = json.loads(object_content)
        
                    # Loop through the array of objects
                    for obj in data:
                        # Make a request to the API Gateway for each object
                        response = request.post(api_gateway_url, json=obj["s3"]["object"])

                        # send JSON object to API-gateway if successfully downloaded
                        if response.status == 200:
                            json_data = json.loads(response.read().decode('utf-8'))
                            filename = f"output_report_{time()}.txt"

                            # Return status codes depending on api_response
                            return {
                                'statusCode': 200,
                                'body': 'Successfully sent JSON data to the API Gateway.',
                                'json': json_data,
                                'file': filename
                            }
                        else:
                            # Construct JSON object to be sent to the output bucket
                            request_id = str(uuid.uuid4())
                            payload_for_output_bucket = {
                                "timestamp": filename,
                                "level": json_data,
                                "request": {
                                    "x-request-id": request_id,
                                    "x-correlation-id": request_id
                                }
                            }

                            # Send payload as JSON string to output bucket with failures
                            output_bucket.put_object(Body=payload_for_output_bucket, Key="body")

                            return {
                                'statusCode': response.status,
                                'body': 'Error sending JSON data to the API Gateway.'
                            }
                    else:
                        return {
                            'statusCode': response.status,
                            'body': 'Error fetching JSON object from S3.'
                        }
                except Exception as e:
                    return {
                        'statusCode': 500,
                        'body': str(e)
                    }

    # Return an error response if the event structure is not as expected
    return {
        'statusCode': 400,
        'body': 'Invalid _event structure. Make sure the _event contains the expected keys and attributes.'
    }
