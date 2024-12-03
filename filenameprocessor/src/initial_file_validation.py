"""Functions for initial file validation"""

import logging
from datetime import datetime
from constants import Constants
from utils_for_filenameprocessor import extract_file_key_elements

logger = logging.getLogger()


def is_valid_datetime(timestamp: str) -> bool:
    """
    Returns a bool to indicate whether the timestamp is a valid datetime in the format 'YYYYmmddTHHMMSSzz'
    where 'zz' is a two digit number indicating the timezone
    """
    # Check that datetime (excluding timezone) is a valid datetime in the expected format.
    if len(timestamp) < 15:
        return False

    # Note that any digits after the seconds (i.e. from the 16th character onwards, usually expected to represent
    # timezone), do not need to be validated
    try:
        datetime.strptime(timestamp[:15], "%Y%m%dT%H%M%S")
    except ValueError:
        return False

    return True


def initial_file_validation(file_key: str) -> bool:
    """
    Returns True if all elements of file key are valid, content headers are valid and the supplier has the
    appropriate permissions. Else returns False.
    """
    # Validate file name format (must contain four '_' a single '.' which occurs after the four '_'

    # Extract elements from the file key
    file_key_elements = extract_file_key_elements(file_key)
    supplier = file_key_elements["supplier"]
    vaccine_type = file_key_elements["vaccine_type"]

    # Validate each file key element
    if not (
        vaccine_type in Constants.VALID_VACCINE_TYPES
        and file_key_elements["vaccination"] == "VACCINATIONS"
        and file_key_elements["version"] in Constants.VALID_VERSIONS
        and supplier  # Note that if supplier could be identified, this also implies that ODS code is valid
        and is_valid_datetime(file_key_elements["timestamp"])
        and file_key_elements["extension"] == "CSV"
    ):
        logger.error("Initial file validation failed: invalid file key")
        raise Exception("Initial file validation failed: invalid file key")

    return vaccine_type, supplier
