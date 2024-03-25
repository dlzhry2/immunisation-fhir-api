import logging
import time
from functools import wraps

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def timed(func):
    """This decorator logs the execution time for the decorated function along with additional details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Assuming correlation_id and request_id are passed as keyword arguments to the functions
        # If they are not, you'll need to modify this part to fetch them from the correct location
        correlation_id = kwargs.get('correlation_id', 'Unknown')
        request_id = kwargs.get('request_id', 'Unknown')

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        # Construct the log message as a structured dictionary
        log = {
            "function": func.__name__,
            "time_taken": f"{round(end - start, 5)}s",
            "correlation_id": correlation_id,
            "request_id": request_id
        }
        logger.info("Function execution details", extra=log)
        return result

    return wrapper
