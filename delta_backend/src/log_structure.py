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
        print(f"Event: {event}")
        logger.info("Starting Delta Handler")
        log_data = {
                'function_name': 'delta_sync',
                'date_time': str(datetime.now())                              
        }

        try:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            log_data['time_taken']= f"{round(end - start, 5)}s"
            status = '500'
            status_code = 'Exception'
            print(f"result: {result}")
            if isinstance(result, dict):
                if str(result["statusCode"]) == "200":
                    status = '201'
                    status_code = 'Processed successfully'
            operation_outcome = {
                'status': status,
                'status_code': status_code
            }
            log_data['operation_outcome'] = operation_outcome
            logger.info(json.dumps(log_data))
            firehose_log = dict()
            firehose_log['event'] = log_data
            firehose_logger.send_log(firehose_log)

            return result

        except Exception as e:
            log_data['error'] = str(e)
            logger.exception(json.dumps(log_data))
            firehose_log = dict()
            firehose_log['event'] = log_data
            firehose_logger.send_log(firehose_log)
            raise

    return wrapper
