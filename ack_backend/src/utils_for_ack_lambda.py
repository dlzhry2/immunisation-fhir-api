"""Utils for ack lambda"""

import os
from clients import s3_client


def get_environment() -> str:
    """Returns the current environment. Defaults to internal-dev for pr and user environments"""
    _env = os.getenv("ENVIRONMENT")
    # default to internal-dev for pr and user environments
    return _env if _env in ["internal-dev", "int", "ref", "sandbox", "prod"] else "internal-dev"


def get_row_count(bucket_name: str, key: str) -> int:
    """Returns the count of the number of lines in the file at the given key, in the source bucket."""
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    return sum(1 for line in response["Body"].iter_lines() if line.strip())
