import unittest
import sys
import os


def get_tests(suite):
    """Recursively fetch all test cases from the test suite."""
    tests = []
    for unit_test in suite:
        if isinstance(unit_test, unittest.TestSuite):
            tests.extend(get_tests(unit_test))
        else:
            test_case = f"{unit_test.__class__.__module__}.{unit_test.__class__.__name__}.{unit_test._testMethodName}"
            tests.append(test_case)
    return tests


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_test_cases.py <test_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    if not os.path.isfile(test_file):
        print(f"Error: File '{test_file}' does not exist.")
        sys.exit(1)

    test_module = os.path.splitext(os.path.basename(test_file))[0]

    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_module)
        test_cases = get_tests(suite)

        if test_cases:
            print("\n".join(test_cases))
        else:
            print(f"No test cases found in '{test_file}'", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error while loading test cases from '{test_file}': {e}", file=sys.stderr)
        sys.exit(1)
