# extract_test_cases.py
import unittest
import sys
import os

def get_tests(suite):
    """Recursively fetch all test cases from the test suite."""
    tests = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            tests.extend(get_tests(test))
        else:
            tests.append(str(test))
    return tests

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_test_cases.py <test_file>")
        sys.exit(1)

    test_file = sys.argv[1]
    if not os.path.isfile(test_file):
        print(f"Error: File '{test_file}' does not exist.")
        sys.exit(1)

    # Load and discover tests from the specified file
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern=os.path.basename(test_file))

    try:
        test_cases = get_tests(suite)
        print('\n'.join(test_cases))
    except Exception as e:
        print(f"Error while loading test cases: {e}", file=sys.stderr)
        sys.exit(1)
