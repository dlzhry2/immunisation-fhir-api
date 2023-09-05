import os
import tempfile
from time import time
from io import BytesIO
from boto3 import resource


def lambda_handler(_event, _context):
    s3_resource = resource('s3')
    output_bucket = s3_resource.Bucket("destination")

    # Create a temporary dir to write our output file to, this avoids polluting /tmp with test files.
    # Using the context manager here ensures the temp dir is cleaned up when the with statement is closed.
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Write some placeholder data to a file in the bucket,
        # so we can test that the lambda writes to the correct output bucket.
        filename = f"output_report_{time()}.txt"
        data = 'Test file to see if the lambda writes to the correct s3 bucket. '
        'If our AWS bill skyrockets, this file has been written to the wrong bucket!'

        # Upload the output file to our destination S3 bucket
        file_obj = BytesIO(data)
        output_bucket.upload_fileobj(file_obj, output_bucket, filename)

    return {
        'statusCode': 200
    }
