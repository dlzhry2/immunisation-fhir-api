from collections import OrderedDict

import copy
from typing import List

from batch.decorators import ImmunizationDecorator, decorate_patient, decorate_vaccination, decorate_vaccine, \
    decorate_questionare, decorate_practitioner
from batch.errors import DecoratorError, TransformerRowError, TransformerUnhandledError

"""Transform the raw records into FHIR immunization resource
Design notes: The record stays as a OrderedDict to preserve the order of the fields. At no point we impose
type constraints on the fields or the record as a whole. This is because the batch data can contain legacy data and data
with various quality. A handle_* function receives a dictionary of current immunization object and adds the appropriate
fields to it. This handle function is also in charge of validation if any and raises an exception. The caller will
collect the exceptions and carries on. So at then end we either have a list of errors with raises the final exception or
we return immunization object.
"""

RecordDict = OrderedDict[str, str]
"""A record of fields with the same order as headers"""


class DataRecordTransformer:
    raw_record: OrderedDict
    raw_imms: dict
    decorators: List[ImmunizationDecorator]
    errors: List[Exception]

    def __init__(self):
        # Initialise the immunization resource with the base model
        self.raw_imms = {
            "resourceType": "Immunization",
            "contained": [],
            "extension": [],
            "performer": [],
        }
        # Set all decorators. NOTE: If you create a new one, then remember to add it here
        self.decorators = [
            decorate_patient,
            decorate_vaccine,
            decorate_vaccination,
            decorate_practitioner,
            decorate_questionare,
        ]

    def transform(self, record: RecordDict) -> dict:
        imms = copy.deepcopy(self.raw_imms)

        tran_err: List[DecoratorError] = []
        for decorator in self.decorators:
            try:
                dec_err = decorator(imms, record)
                if dec_err:
                    tran_err.append(dec_err)
            except Exception as e:
                raise TransformerUnhandledError(decorator_name=str(decorator)) from e

        if tran_err:
            raise TransformerRowError(errors=tran_err)

        return imms
