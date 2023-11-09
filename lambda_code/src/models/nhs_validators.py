from models.constants import Constants


class NHSValidators:
    """NHS specific validator methods"""

    @staticmethod
    def validate_nhs_number(nhs_number):
        """Validate NHS Number"""
        if nhs_number:
            nhs_number = nhs_number.replace(" ", "")
            if len(nhs_number) != 10:
                raise ValueError("NHS Number must be 10 digits long")

        return nhs_number

    @staticmethod
    def validate_person_dob(person_dob):
        """Validate Person DOB"""
        if person_dob:
            parsed_date = Constants.convert_to_date(person_dob)
            return parsed_date
        return None

    @staticmethod
    def validate_person_gender_code(person_gender_code):
        """Validate Person Gender Code"""

        if person_gender_code:
            if person_gender_code not in Constants.person_gender_codes:
                raise ValueError(
                    "Invalid value for PERSON_GENDER_CODE. It must be 0, 1, 2, or 9."
                )
            return person_gender_code
        return None

    @staticmethod
    def validate_person_postcode(person_postcode):
        """Validate Person Postcode"""
        if person_postcode:
            postcode = person_postcode.replace(" ", "")
            if len(postcode) > 8:
                raise ValueError("PERSON_POSTCODE must be less that 8 characters.")
        return person_postcode

    @staticmethod
    def validate_date_and_time(date_and_time):
        """Validate Date and Time"""
        if not date_and_time:
            raise ValueError("DATE_AND_TIME is a mandatory field.")
        parsed_datetime = Constants.convert_iso8601_to_datetime(date_and_time)
        return parsed_datetime

    @staticmethod
    def validate_site_code(site_code):
        """Validate Site Code"""
        if not site_code:
            raise ValueError("SITE_CODE is a mandatory field.")

        if Constants.is_urn_resource(site_code):
            raise ValueError("SITE_CODE must not be a urn code")

        return site_code

    @staticmethod
    def validate_action_flag(action_flag):
        """Validate Action Flag"""
        if not action_flag:
            raise ValueError("ACTION_FLAG is a mandatory field.")

        if action_flag not in Constants.action_flags:
            raise ValueError("ACTION_FLAG should be completed or entered-in-error")

        return action_flag

    @staticmethod
    def validate_performing_professional_forename(
        performing_professional_forename, performing_professional_surname
    ):
        """Validate performing professional forename"""
        if performing_professional_forename:
            if not performing_professional_surname:
                raise ValueError(
                    "If PERFORMING_PROFESSIONAL_FORENAME is given, \
                        PERFORMING_PROFESSIONAL_SURNAME must also be given"
                )
            return performing_professional_forename
        if performing_professional_surname:
            raise ValueError(
                "If PERFORMING_PROFESSIONAL_SURNAME is given, \
                    PERFORMING_PROFESSIONAL_FORENAME must also be given"
            )

    @staticmethod
    def validate_performing_professional_body_reg_code(
        performing_professional_body_reg_code, performing_professional_body_reg_uri
    ):
        """Validate performing professional body reg code"""
        if performing_professional_body_reg_code:
            if not performing_professional_body_reg_uri:
                raise ValueError(
                    "If PERFORMING_PROFESSIONAL_BODY_REG_CODE is given, \
                        PERFORMING_PROFESSIONAL_BODY_REG_URI must also be given"
                )

            return performing_professional_body_reg_code

    @staticmethod
    def validate_recorded_date(recorded_date):
        """Validate recorded date"""
        if recorded_date:
            parsed_date = Constants.convert_to_date(recorded_date)
            return parsed_date
        return None

    @staticmethod
    def validate_report_origin(report_origin, primary_source):
        """Validate report origin"""
        if primary_source and not report_origin:
            raise ValueError(
                "REPORT_ORIGIN is a mandatory field, when PRIMARY_SOURCE is given"
            )
        return report_origin

    @staticmethod
    def validate_not_given(not_given):
        """Validate not given flag"""
        if not_given:
            if not (
                not_given == Constants.vaccination_not_given_flag
                or not_given == Constants.vaccination_given_flag
            ):
                raise ValueError("NOT_GIVEN flag should be 'empty' or 'not-done'")
        return not_given

    @staticmethod
    def validate_vaccination_procedure_code(vaccination_procedure_code, not_given):
        """Validate vaccination procedure code"""
        if not_given:
            if (
                not Constants.if_vaccine_not_give(not_given)
                and not vaccination_procedure_code
            ):
                raise ValueError(
                    "VACCINATION_PROCEDURE_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return vaccination_procedure_code

    @staticmethod
    def validate_vaccination_situation_code(vaccination_situation_code, not_given):
        """Validate vaccination situation code"""
        if not_given:
            if (
                Constants.if_vaccine_not_give(not_given)
                and not vaccination_situation_code
            ):
                raise ValueError(
                    "VACCINATION_SITUATION_CODE is a mandatory field, when NOT_GIVEN=TRUE"
                )
        return vaccination_situation_code

    @staticmethod
    def validate_reason_not_given_code(reason_not_given_code, not_given):
        """Validate reason not given code"""
        if not_given:
            if Constants.if_vaccine_not_give(not_given) and not reason_not_given_code:
                raise ValueError(
                    "REASON_NOT_GIVEN_CODE is a mandatory field, when NOT_GIVEN=TRUE"
                )
        return reason_not_given_code

    @staticmethod
    def validate_dose_sequence(dose_sequence, not_given):
        """Validate dose sequence"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not dose_sequence:
                raise ValueError(
                    "DOSE_SEQUENCE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return dose_sequence

    @staticmethod
    def validate_vaccine_product_code(vaccine_product_code, not_given):
        """Validate vaccine product code"""
        if not_given:
            if (
                not Constants.if_vaccine_not_give(not_given)
                and not vaccine_product_code
            ):
                raise ValueError(
                    "VACCINE_PRODUCT_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return vaccine_product_code

    @staticmethod
    def validate_vaccine_manufacturer(vaccine_manufacturer, not_given):
        """Validate vaccine manufacturer"""
        if not_given:
            if (
                not Constants.if_vaccine_not_give(not_given)
                and not vaccine_manufacturer
            ):
                raise ValueError(
                    "VACCINE_MANUFACTURER is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return vaccine_manufacturer

    @staticmethod
    def validate_batch_number(batch_number, not_given):
        """Validate batch number"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not batch_number:
                raise ValueError(
                    "VACCINE_BATCH_NUMBER is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return batch_number

    @staticmethod
    def validate_expiry_date(expiry_date, not_given):
        """Validate expiry date"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not expiry_date:
                raise ValueError(
                    "EXPIRY_DATE is a mandatory field, when NOT_GIVEN=FALSE"
                )
            parsed_date = Constants.convert_to_date(expiry_date)
            return parsed_date

    @staticmethod
    def validate_route_of_vaccination_code(route_of_vaccination_code, not_given):
        """Validate route of vaccination code"""
        if not_given:
            if (
                not Constants.if_vaccine_not_give(not_given)
                and not route_of_vaccination_code
            ):
                raise ValueError(
                    "ROUTE_OF_VACCINATION_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return route_of_vaccination_code

    @staticmethod
    def validate_dose_amount(dose_amount, not_given):
        """Validate dose amount"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not dose_amount:
                raise ValueError(
                    "DOSE_AMOUNT is a mandatory field, when NOT_GIVEN=FALSE"
                )
            if not Constants.has_max_decimal_places(dose_amount):
                raise ValueError("DOSE_AMOUNT must have a maximum of 4 decimal places")
            return dose_amount
        return None

    @staticmethod
    def validate_dose_unit_code(dose_unit_code, not_given):
        """Validate dose unit code"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not dose_unit_code:
                raise ValueError(
                    "DOSE_UNIT_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return dose_unit_code

    @staticmethod
    def validate_indication_code(indication_code, not_given):
        """Validate indication code"""
        if not_given:
            if not Constants.if_vaccine_not_give(not_given) and not indication_code:
                raise ValueError(
                    "INDICATION_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return indication_code

    @staticmethod
    def validate_consent_for_treatment_code(consent_for_treatment_code, not_given):
        """Validate consent for treatment code"""
        if not_given:
            if (
                not Constants.if_vaccine_not_give(not_given)
                and not consent_for_treatment_code
            ):
                raise ValueError(
                    "CONSENT_FOR_TREATMENT_CODE is a mandatory field, when NOT_GIVEN=FALSE"
                )
        return consent_for_treatment_code

    @staticmethod
    def validate_submitted_timestamp(submitted_timestamp):
        """Validate submitted timestamp"""
        if submitted_timestamp:
            parsed_datetime = Constants.convert_iso8601_to_datetime(submitted_timestamp)
            return parsed_datetime

    @staticmethod
    def validate_location_code(location_code):
        """Validate location code"""
        if location_code:
            postcode = location_code.replace(" ", "")
            if len(postcode) > 8:
                raise ValueError("LOCATION_CODE must be less than 8 characters.")
            return location_code
        return "X99999"

    @staticmethod
    def validate_reduce_validation_code(
        reduce_validation_code, reduce_validation_reason
    ):
        """Validate reduce validation code"""
        if reduce_validation_code == "True":
            if not reduce_validation_reason:
                raise ValueError(
                    "REDUCE_VALIDATION_REASON is a mandatory field, \
                        when REDUCE_VALIDATION_CODE is True"
                )
            return True
        return False
