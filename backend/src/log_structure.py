import logging
import time
from functools import wraps

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")

def function_info(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        event = args[0] if args else {}
        headers = event.get('headers', {})
        correlation_id = headers.get('X-Correlation-ID', 'X-Correlation-ID not passed')
        request_id = headers.get('X-Request-ID', 'X-Request-ID not passed')
        actual_path = event.get('path', 'Unknown')
        resource_path = event.get('requestContext', {}).get('resourcePath', 'Unknown')
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log = {
            "function_name": func.__name__,
            "time_taken":"{} ran in {}s".format(func.__name__, round(end - start, 5)),
            "X-Correlation-ID": correlation_id,
            "X-Request-ID": request_id,
            "actual_path": actual_path,
            "resource_path": resource_path
            }
        logger.info("Function execution details: %s", log)
        return result

    return wrapper
