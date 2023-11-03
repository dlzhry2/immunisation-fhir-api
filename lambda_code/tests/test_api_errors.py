import os
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.errors import ApiError, Severity, Code


class TestApiErrors(unittest.TestCase):
    def test_error_to_uk_core(self):
        code = Code.not_found
        severity = Severity.error
        diag = "a-diagnostic"
        error_id = "a-id"

        api_error = ApiError(id=error_id, severity=severity, code=code, diagnostics=diag)
        error = api_error.to_uk_core().dict()

        issue = error["issue"][0]
        self.assertEqual(error["id"], error_id)
        self.assertEqual(issue["code"], "not_found")
        self.assertEqual(issue["severity"], "error")
        self.assertEqual(issue["diagnostics"], diag)
        self.assertEqual(issue["details"]["coding"][0]["code"], "NOT_FOUND")
