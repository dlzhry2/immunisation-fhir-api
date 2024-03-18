from collections import OrderedDict

import copy
from dataclasses import dataclass
from enum import Enum
from typing import List

from batch.decorators import ImmunizationDecorator, decorate_patient, decorate_vaccination, decorate_vaccine, \
    decorate_questionare, decorate_practitioner
from batch.errors import DecoratorError, TransformerRowError, DecoratorUnhandledError

"""Transform the raw records into FHIR immunization resource
Design notes: The record stays as a OrderedDict to preserve the order of the fields. At no point we impose
type constraints on the fields or the record as a whole. This is because the batch data can contain legacy data and data
with various quality. A handle_* function receives a dictionary of current immunization object and adds the appropriate
fields to it. This handle function is also in charge of validation if any and raises an exception. The caller will
collect the exceptions and carries on. So at then end we either have a list of errors with raises the final exception or
we return immunization object.
"""


class FieldName(str, Enum):
    nhs_number = "NHS_NUMBER"
    person_forename = "PERSON_FORENAME"
    person_surname = "PERSON_SURNAME"
    person_dob = "PERSON_DOB"
    person_gender_code = "PERSON_GENDER_CODE"
    person_postcode = "PERSON_POSTCODE"
    date_and_time = "DATE_AND_TIME"
    site_code = "SITE_CODE"
    unique_id = "UNIQUE_ID"
    unique_id_uri = "UNIQUE_ID_URI"
    action_flag = "ACTION_FLAG"
    performing_professional_forename = "PERFORMING_PROFESSIONAL_FORENAME"
    performing_professional_surname = "PERFORMING_PROFESSIONAL_SURNAME"
    performing_professional_body_reg_code = "PERFORMING_PROFESSIONAL_BODY_REG_CODE"
    performing_professional_body_reg_uri = "PERFORMING_PROFESSIONAL_BODY_REG_URI"
    sds_job_role_name = "SDS_JOB_ROLE_NAME"
    recorded_date = "RECORDED_DATE"
    primary_source = "PRIMARY_SOURCE"
    report_origin = "REPORT_ORIGIN"
    vaccination_procedure_code = "VACCINATION_PROCEDURE_CODE"
    vaccination_procedure_term = "VACCINATION_PROCEDURE_TERM"
    vaccination_situation_code = "VACCINATION_SITUATION_CODE"
    vaccination_situation_term = "VACCINATION_SITUATION_TERM"
    not_given = "NOT_GIVEN"
    reason_not_given_code = "REASON_NOT_GIVEN_CODE"
    reason_not_given_term = "REASON_NOT_GIVEN_TERM"
    dose_sequence = "DOSE_SEQUENCE"
    vaccine_product_code = "VACCINE_PRODUCT_CODE"
    vaccine_product_term = "VACCINE_PRODUCT_TERM"
    vaccine_manufacturer = "VACCINE_MANUFACTURER"
    batch_number = "BATCH_NUMBER"
    expiry_date = "EXPIRY_DATE"
    site_of_vaccination_code = "SITE_OF_VACCINATION_CODE"
    site_of_vaccination_term = "SITE_OF_VACCINATION_TERM"
    route_of_vaccination_code = "ROUTE_OF_VACCINATION_CODE"
    route_of_vaccination_term = "ROUTE_OF_VACCINATION_TERM"
    dose_amount = "DOSE_AMOUNT"
    dose_unit_code = "DOSE_UNIT_CODE"
    dose_unit_term = "DOSE_UNIT_TERM"
    indication_code = "INDICATION_CODE"
    indication_term = "INDICATION_TERM"
    nhs_number_status_indicator_code = "NHS_NUMBER_STATUS_INDICATOR_CODE"
    nhs_number_status_indicator_description = "NHS_NUMBER_STATUS_INDICATOR_DESCRIPTION"
    site_code_type_uri = "SITE_CODE_TYPE_URI"
    local_patient_id = "LOCAL_PATIENT_ID"
    local_patient_uri = "LOCAL_PATIENT_URI"
    consent_for_treatment_code = "CONSENT_FOR_TREATMENT_CODE"
    consent_for_treatment_description = "CONSENT_FOR_TREATMENT_DESCRIPTION"
    care_setting_type_code = "CARE_SETTING_TYPE_CODE"
    care_setting_type_description = "CARE_SETTING_TYPE_DESCRIPTION"
    ip_address = "IP_ADDRESS"
    user_id = "USER_ID"
    user_name = "USER_NAME"
    user_email = "USER_EMAIL"
    submitted_timestamp = "SUBMITTED_TIMESTAMP"
    location_code = "LOCATION_CODE"
    location_code_type_uri = "LOCATION_CODE_TYPE_URI"


@dataclass
class Record:
    pass
    # nhs_number: str
    # person_forename: str
    # person_surname: str
    # person_dob: str
    # person_gender_code: str
    # person_postcode: str
    # date_and_time: str
    # site_code: str
    # unique_id: str
    # unique_id_uri: str
    # action_flag: str
    # performing_professional_forename: str
    # performing_professional_surname: str
    # performing_professional_body_reg_code: str
    # performing_professional_body_reg_uri: str
    # sds_job_role_name: str
    # recorded_date: str
    # primary_source: str
    # report_origin: str
    # vaccination_procedure_code: str
    # vaccination_procedure_term: str
    # vaccination_situation_code: str
    # vaccination_situation_term: str
    # not_given: str
    # reason_not_given_code: str
    # reason_not_given_term: str
    # dose_sequence: str
    # vaccine_product_code: str
    # vaccine_product_term: str
    # vaccine_manufacturer: str
    # batch_number: str
    # expiry_date: str
    # site_of_vaccination_code: str
    # site_of_vaccination_term: str
    # route_of_vaccination_code: str
    # route_of_vaccination_term: str
    # dose_amount: str
    # dose_unit_code: str
    # dose_unit_term: str
    # indication_code: str
    # indication_term: str
    # nhs_number_status_indicator_code: str
    # nhs_number_status_indicator_description: str
    # site_code_type_uri: str
    # local_patient_id: str
    # local_patient_uri: str
    # consent_for_treatment_code: str
    # consent_for_treatment_description: str
    # care_setting_type_code: str
    # care_setting_type_description: str
    # ip_address: str
    # user_id: str
    # user_name: str
    # user_email: str
    # submitted_timestamp: str
    # location_code: str
    # location_code_type_uri: str

    # def __init__(self, raw_record: RawRecord):
    #     for i, header in enumerate(field_name_values):
    #         setattr(self, header.tolower(), raw_record[i])


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
                raise DecoratorUnhandledError(decorator_name=str(decorator)) from e

        if tran_err:
            raise TransformerRowError(errors=tran_err)

        return imms
