""" Convert Immunisation CSV data to Immunization Model """

import csv
from typing import Union
from datetime import datetime
from pydantic import ValidationError
from models.immunization import ImmunizationModel
from models.failures import ImmunizationErrorModel


def parse_iso8601_datetime(iso_datetime: str) -> Union[str, None]:
    """
    Parse an ISO 8601 datetime string with timezone offset and format it
    to YYYY-MM-DDThh:mm:ss+zz.
    """
    try:
        dt = datetime.fromisoformat(iso_datetime)
        dt = dt.astimezone()

        # Get just the offset so we can format it correctly (from +0000 to +00:00)
        # In python 3.12 we can use the %:z format rather than %z
        tz = dt.strftime("%z")
        tz = f"{tz[:3]}:{tz[3:]}"

        # Format the datetime string without the timezone offset
        dt = dt.strftime("%Y-%m-%dT%H:%M:%S")
        dt = f"{dt}{tz}"

        return dt
    except ValueError:
        return None


def generate_failed_record(row: dict, reasons: str) -> ImmunizationErrorModel:
    """Format an exception into a record"""
    failed_record = {
        "NHS_NUMBER": row.get("NHS_NUMBER", None),
        "UNIQUE_ID": row.get("UNIQUE_ID", None),
        "FAILURE_REASONS": reasons,
    }

    immunisation_failure = ImmunizationErrorModel(**failed_record)

    return immunisation_failure


def read_csv_to_immunizations(
    csv_data: str,
) -> Union[list[ImmunizationModel], list[ImmunizationErrorModel]]:
    """Read a CSV file and return a list of ImmunizationModel objects"""
    immunizations = []
    failures = []

    csv_reader = csv.DictReader(csv_data.splitlines())
    for row in csv_reader:
        try:
            # Parse datetime fields if needed
            if row["PERSON_DOB"]:
                row["PERSON_DOB"] = str(
                    datetime.strptime(row["PERSON_DOB"], "%Y-%m-%d").date()
                )
            if row["DATE_AND_TIME"]:
                row["DATE_AND_TIME"] = parse_iso8601_datetime(row["DATE_AND_TIME"])
            if row["RECORDED_DATE"]:
                row["RECORDED_DATE"] = str(
                    datetime.strptime(row["RECORDED_DATE"], "%Y-%m-%d").date()
                )
            if row["EXPIRY_DATE"]:
                row["EXPIRY_DATE"] = str(
                    datetime.strptime(row["EXPIRY_DATE"], "%Y-%m-%d").date()
                )
            immunization = ImmunizationModel(**row)
            if immunization is not None:
                immunizations.append(immunization)

        except ValidationError as failure:
            # ValidationError's errors() method returns a list of errors
            reasons = failure.errors()
            immunisation_failure = generate_failed_record(row, reasons)
            failures.append(immunisation_failure)

        except ValueError as failure:
            # ValueError just returns a string for the error so we'll add it to a list
            reasons = [str(failure)]
            immunisation_failure = generate_failed_record(row, reasons)
            failures.append(immunisation_failure)

        except Exception as failure:
            # A catch all for anything else that might go wrong
            reasons = [str(failure)]
            immunisation_failure = generate_failed_record(row, reasons)
            failures.append(immunisation_failure)

    return immunizations, failures
