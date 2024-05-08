import logging
import json
import time
from datetime import datetime
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
        log_data = {
                'function_name': func.__name__,
                'date_time': str(datetime.now()),
                'X-Correlation-ID': correlation_id,
                'X-Request-ID': request_id,
                'actual_path': actual_path,
                'resource_path': resource_path                
        }

        try:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            log_data['time_taken']= f"{round(end - start, 5)}s"
            status = "201"
            status_code = "Completed successfully"
            diagnostics = ""
            if isinstance(result, dict):
                status = result["statusCode"]
                if result.get("body"):
                    ops_outcome = json.loads(result["body"])
                    outcome_body = ops_outcome["issue"][0]
                    status_code = outcome_body["code"]
                    diagnostics = outcome_body["diagnostics"]
            operation_outcome = {
                'status': status,
                'status_code': status_code
            }
            if len(diagnostics) > 1:
                operation_outcome['diagnostics'] = diagnostics
            log_data['operation_outcome'] = operation_outcome
            logger.info(json.dumps(log_data))
            firehose_log = dict()
            firehose_log['event'] = log_data
            firehose_logger.send_log(firehose_log)

            return result

        except Exception as e:
            log_data['error'] = str(e)
            logger.exception(json.dumps(log_data))
            firehose_log['event'] = log_data
            firehose_logger.send_log(firehose_log)
            raise

    return wrapper
