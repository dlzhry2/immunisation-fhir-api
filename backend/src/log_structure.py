import boto3
import logging
import json
import os
import time
from botocore.config import Config
from functools import wraps
from log_firehose import FirehoseLogger

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")


firehose_logger = FirehoseLogger()


def function_info(func):
    """This decorator prints the execution information for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        event = args[0] if args else {}
        headers = event.get("headers", {})
        correlation_id = headers.get("X-Correlation-ID", "X-Correlation-ID not passed")
        request_id = headers.get("X-Request-ID", "X-Request-ID not passed")
        actual_path = event.get("path", "Unknown")
        resource_path = event.get("requestContext", {}).get("resourcePath", "Unknown")
        logger.info(
            f"Starting {func.__name__} with X-Correlation-ID: {correlation_id} and X-Request-ID: {request_id}"
        )

        try:
            start = time.time()
            result = func(*args, **kwargs)
            outcome = "500"

            if isinstance(result, dict):
                outcome = result["statusCode"]

            end = time.time()
            logData = {
                "event": {
                    "function_name": func.__name__,
                    "time_taken": f"{round(end - start, 5)}s",
                    "X-Correlation-ID": correlation_id,
                    "X-Request-ID": request_id,
                    "actual_path": actual_path,
                    "resource_path": resource_path,
                    "status": outcome,
                    "status_code": "Completed successfully",
                }
            }
            logger.info(logData)
            firehose_logger.send_log(logData)

            return result

        except Exception as e:
            logData = {
                "event": {
                    "function_name": func.__name__,
                    "time_taken": f"{round(time.time() - start, 5)}s",
                    "X-Correlation-ID": correlation_id,
                    "X-Request-ID": request_id,
                    "actual_path": actual_path,
                    "resource_path": resource_path,
                    "error": str(e),
                }
            }

            logger.exception(logData)
            firehose_logger.send_log(logData)
            raise

    return wrapper
