from dataclasses import dataclass
from typing import List


@dataclass
class BatchErrorBase(RuntimeError):
    pass


class NoneThrowingError:
    """A base class to mark errors that should not be thrown."""


@dataclass
class RowError(BatchErrorBase):
    row: int


@dataclass
class RowMismatchError(BatchErrorBase):
    pass


@dataclass
class TransformerFieldError(NoneThrowingError):
    """An error that occurs during transformation of a field or a collection of fields like patient"""
    message: str


@dataclass
class DecoratorError(NoneThrowingError):
    """An error that accumulates all the errors that occur during decoration.
    It contains a collection of all field errors in the row."""
    errors: List[TransformerFieldError]
    decorator_name: str


@dataclass
class DecoratorUnhandledError(RuntimeError):
    """An error that occurs when a decorator throws an error.
    A decorator should not throw an error. So any Exception is considered an unhandled error.
    NOTE: This differentiation is so we can identify bugs in handling CSV data or when we are dealing with unknown CSV.
    """
    decorator_name: str


@dataclass
class TransformerRowError(RuntimeError):
    """An error that occurs during transformation of a row. It contains a collection of all decorators."""
    errors: List[DecoratorError]


@dataclass
class TransformerError(BatchErrorBase):
    """An error that occurs during transformation of a batch file.
    It contains a collection of all row errors in the batch task.
    This is the error that will be used to generate the final error report."""
    errors: List[TransformerRowError]
