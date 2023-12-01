""" Convert Immunisation CSV data to Immunization Model """
import csv
from typing import Union, List

from pydantic import ValidationError


from models.csv_immunization import CsvImmunizationModel
from models.failures import CsvImmunizationErrorModel


def generate_failed_record(row: dict, reasons: str) -> CsvImmunizationErrorModel:
    """Format an exception into a record"""
    failed_record = {
        "nhs_number": row.get("NHS_NUMBER", None),
        "unique_id": row.get("UNIQUE_ID", None),
        "failure_reasons": reasons,
    }

    immunisation_failure = CsvImmunizationErrorModel(**failed_record)

    return immunisation_failure


def read_csv_to_model(
    csv_data: str,
) -> Union[List[CsvImmunizationModel], List[CsvImmunizationErrorModel]]:
    """Read a CSV file and return a list of ImmunizationModel objects"""
    immunizations = []
    failures = []

    csv_reader = csv.DictReader(csv_data.splitlines())
    for row in csv_reader:
        try:
            # Filter out unwanted fields
            imms = CsvImmunizationModel(**row)
            immunizations.append(imms)
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
