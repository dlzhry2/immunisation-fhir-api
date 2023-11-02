import unittest
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.errors import ApiError, Severity, Code


class TestApiErrors(unittest.TestCase):
    def test_event_not_found(self):
        a = ApiError(id="foo", severity=Severity.error, code=Code.not_found, diagnostics="bad thing happened")
        print(a.dict())
        # print(ApiErrors.event_not_found("foo").json())
