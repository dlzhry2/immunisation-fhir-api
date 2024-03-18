from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    UNHANDLED = "unhandled"
    HANDLED = "handled"


@dataclass
class LogData:
    row: int = -1
    error_type: ErrorType = None


class BatchLogger:
    def __init__(self):
        pass

    def log(self, log_data: LogData, exp: Exception = None):
        pass

    def log_error(self, log_data: LogData, exp: Exception):
        pass
