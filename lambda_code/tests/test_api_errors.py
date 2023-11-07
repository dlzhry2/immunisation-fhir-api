import os
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from models.errors import Severity, Code, create_operation_outcome


class TestApiErrors(unittest.TestCase):
    def test_error_to_uk_core2(self):
        code = Code.not_found

        severity = Severity.error
        diag = "a-diagnostic"
        error_id = "a-id"

        error = create_operation_outcome(resource_id=error_id, severity=severity, code=code, diagnostics=diag).dict()

        issue = error["issue"][0]
        self.assertEqual(error["id"], error_id)
        self.assertEqual(issue["code"], "not-found")
        self.assertEqual(issue["severity"], "error")
        self.assertEqual(issue["diagnostics"], diag)
        self.assertEqual(issue["details"]["coding"][0]["code"], "NOT-FOUND")
