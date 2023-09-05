import os
import tempfile
from time import time
from boto3 import resource


def lambda_handler(_event, _context):
    s3_resource = resource('s3')
    output_bucket = s3_resource.Bucket("destination")
    # Create a temporary dir to write our output file to, this avoids polluting /tmp with test files.
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        # Write some placeholder data to a file, so we can test that the lambda writes to the correct output bucket.
        filename = f"output_report_{time()}.txt"
        data = 'Test file to see if the lambda writes to the correct s3 bucket. '
        'If our AWS bill skyrockets, this file has been written to the wrong bucket!'
        with open(filename, 'w') as f:
            f.write(data)

    output_bucket.upload_fileobj(data, output_bucket, filename)

    return {
        'statusCode': 200
    }
