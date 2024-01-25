"""Store values for use in tests"""
from decimal import Decimal
from dataclasses import dataclass

# Lists of data types for 'invalid data type' testing
integers = [-1, 0, 1]
floats = [-1.3, 0.0, 1.0, 2.5]
decimals = [Decimal("-1"), Decimal("0"), Decimal("1"), Decimal("-1.3"), Decimal("2.5")]
booleans = [True, False]
dicts = [{}, {"InvalidKey": "InvalidValue"}]
lists = [[], ["Invalid"]]
strings = ["", "invalid"]


@dataclass
class InvalidDataTypes:
    """Store lists of invalid data types for tests"""

    for_integers = [None] + floats + decimals + booleans + dicts + lists + strings
    for_decimals_or_integers = [None] + floats + booleans + dicts + lists + strings
    for_booleans = [None] + integers + floats + decimals + dicts + lists + strings
    for_dicts = [None] + integers + floats + decimals + booleans + lists + strings
    for_lists = [None] + integers + decimals + floats + booleans + dicts + strings
    for_strings = [None] + integers + floats + decimals + booleans + dicts + lists


@dataclass
class ValidValues:
    """Store valid values for tests"""

    for_date_times = [
        "2000-01-01T00:00:00+00:00",  # Time and offset all zeroes
        "1933-12-31T11:11:11+12:45",  # Positive offset (with hours and minutes not 0)
        "1933-12-31T11:11:11-05:00",  # Negative offset
        "2000-01-01T00:00:00.000+00:00",  # Time and offset all zeroes with milliseconds
        "1933-12-31T11:11:11.1+12:45",  # Positive offset (with hours and minutes not 0)
        "1933-12-31T11:11:11.111111+12:45",  # Positive offset (with hours and minutes not 0)
    ]

    # Not a valid snomed code, but is valid coding format for format testing
    snomed_coding_element = {
        "system": "http://snomed.info/sct",
        "code": "ABC123",
        "display": "test",
    }


@dataclass
class InvalidValues:
    """Store lists of invalid values for tests"""

    for_postal_codes = [
        "SW1  1AA",  # Too many spaces in divider
        "SW 1 1A",  # Too many space dividers
        "AAA0000AA",  # Too few space dividers
        " AA00 00AA",  # Invalid additional space at start
        "AA00 00AA ",  # Invalid additional space at end
        " AA0000AA",  # Space is incorrectly at start
        "AA0000AA ",  # Space is incorrectly at end
    ]

    for_date_string_formats = [
        # Strings which are not in acceptable date format
        "",  # Empty
        "invalid",  # With letters
        "20000101",  # Without dashes
        "200001-01",  # Missing first dash
        "2000-0101",  # Missing second dash
        "2000:01:01",  # Semi-colons instead of dashes
        "2000-01-011",  # Extra digit at end
        "12000-01-01",  # Extra digit at start
        "12000-01-021",  # Extra digit at start and end
        "99-01-01",  # Year represented without century (i.e. 2 digits instead of 4)
        "01-01-1999",  # DD-MM-YYYY format
        "01-01-99",  # DD-MM-YY format
        # Strings which are in acceptable date format, but are invalid dates
        "2000-00-01",  # Month 0
        "2000-13-01",  # Month 13
        "2000-01-00",  # Day 0
        "2000-01-32",  # Day 32
        "2000-02-30",  # Invalid combnation of month and day
    ]

    # Strings which are not in acceptable date time format
    for_date_time_string_formats = [
        "",  # Empty string
        "invalid",  # Invalid format
        "20000101",  # Date digits only (i.e. without hypens)
        "20000101000000",  # Date and time digits only
        "200001010000000000",  # Date, time and timezone digits only
        "2000-01-01",  # Date only
        "2000-01-01T00:00:00",  # Date and time only
        "2000-01-01T00:00:00+00",  # Date and time with GMT timezone offset only in hours
        "2000-01-01T00:00:00+01",  # Date and time with BST timezone offset only in hours
        "12000-01-01T00:00:00+00:00",  # Extra character at start of string
        "2000-01-01T00:00:00+00:001",  # Extra character at end of string
        "12000-01-02T00:00:00-01:001",  # Extra characters at start and end of string
        "2000-01-0122:22:22+00:00",  # Missing T
        "2000-01-01T222222+00:00",  # Missing time colons
        "2000-01-01T22:22:2200:00",  # Missing timezone indicator
        "2000-01-01T22:22:22-0100",  # Missing timezone colon
        "99-01-01T00:00:00+00:00",  # Missing century (i.e. only 2 digits for year)
        "01-01-2000T00:00:00+00:00",  # Date in wrong order (DD-MM-YYYY)
    ]

    # Strings which are in acceptable date time format, but are invalid dates, times or timezones
    for_date_times = [
        "2000-00-01T00:00:00+00:00",  # Month 00
        "2000-13-01T00:00:00+00:00",  # Month 13
        "2000-01-00T00:00:00+00:00",  # Day 00
        "2000-01-32T00:00:00+00:00",  # Day 32
        "2000-02-30T00:00:00+00:00",  # Invalid month and day combination (30th February)
        "2000-01-01T24:00:00+00:00",  # Hour 24
        "2000-01-01T00:60:00+00:00",  # Minute 60
        "2000-01-01T00:00:60+00:00",  # Second 60
        "2000-01-01T00:00:00+24:00",  # Timezone hour +24
        "2000-01-01T00:00:00-24:00",  # Timezone hour -24
        "2000-01-01T00:00:00+00:60",  # Timezone minute 60
    ]

    for_lists_of_strings_of_length_1 = [[1], [False], [["Test1"]]]

    for_strings_with_max_100_chars = [
        "This is a really long string with more than 100 "
        + "characters to test whether the validator is working well"
    ]
