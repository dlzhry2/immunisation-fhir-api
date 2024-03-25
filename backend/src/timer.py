import logging
import time

from functools import wraps

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel("INFO")


def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        correlation_id = kwargs.get('correlation_id', 'Unknown')
        request_id = kwargs.get('request_id', 'Unknown')
        path = "path"
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log = {
            "function_name": func.__name__,
            "time_taken":"{} ran in {}s".format(func.__name__, round(end - start, 5)),
            "X-Correlation-ID": correlation_id,
            "X-Request-ID": request_id,
            "path": path
            }
        logger.info(log)
        return result

    return wrapper