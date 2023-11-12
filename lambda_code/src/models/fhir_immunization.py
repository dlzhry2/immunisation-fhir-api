# from fhir.resources.immunization import Immunization
from models.nhs_validators import NHSValidators
from icecream import ic
from fhir.resources.R4B.immunization import Immunization


class ImmunizationValidator:
    def __init__(self, json_data) -> None:
        self.json_data = json_data

    @classmethod
    def validate_nhs_number(cls, values):
        """Validate NHS Number"""
        nhs_number = values["patient"].dict()["identifier"]["value"]
        NHSValidators.validate_nhs_number(nhs_number)
        return values

    # TODO: Can't validate yet as DOB is not in the sample data
    @classmethod
    def validate_person_dob(cls, values):
        """Validate Person DOB"""
        dob = values["patient"].dict()["birthDate"]
        NHSValidators.validate_person_dob(dob)
        return values

    # TODO: Can't validate yet as gender code is not in the sample data
    @classmethod
    def validate_person_gender_code(cls, values):
        """Validate Person Gender Code"""
        gender_code = values["patient"].dict()["gender"]
        NHSValidators.validate_person_gender_code(gender_code)
        return values

    # TODO: Can't validate yet as gender code is not in the sample data
    @classmethod
    def validate_person_postcode(self, values):
        """Validate Person Postcode"""
        postcode = values["patient"].dict()["address"][0]["postalCode"]
        NHSValidators.validate_person_postcode(postcode)
        return values

    @classmethod
    def validate_date_and_time(cls, values):
        """Validate Date and Time"""
        date_and_time = values["occurrenceDateTime"]
        NHSValidators.validate_date_and_time(date_and_time)
        return values

    # TODO: Can't validate yet as site code is not in the sample data
    @classmethod
    def validate_site_code(cls, values):
        """Validate Site Code"""
        site_code = values["location"]["identifier"]["value"]
        NHSValidators.validate_site_code(site_code)
        return values

    @classmethod
    def validate_action_flag(cls, values):
        """Validate Action Flag"""
        action_flag = values["status"]
        NHSValidators.validate_action_flag(action_flag)
        return values

    # TODO: Can't validate yet as performing professional forename is not in the sample data
    @classmethod
    def validate_performing_professional_forename(cls, values):
        """Validate Performing Professional Forename"""
        performing_professional_forename = values["performer"][0]["actor"]["name"][0][
            "given"
        ][0]
        performing_professional_surname = values["performer"][0]["actor"]["name"][0][
            "family"
        ]
        NHSValidators.validate_performing_professional_forename(
            performing_professional_forename, performing_professional_surname
        )
        return values

    @classmethod
    def validate_performing_professional_body_reg_code(cls, values):
        """Validate Performing Professional Body Reg Code"""
        performing_professional_body_reg_code = values["performer"][0]["actor"][
            "identifier"
        ]["value"]
        performing_professional_body_reg_uri = values["performer"][0]["actor"][
            "identifier"
        ]["system"]
        NHSValidators.validate_performing_professional_body_reg_code(
            performing_professional_body_reg_code, performing_professional_body_reg_uri
        )
        return values

    @classmethod
    def validate_recorded_date(cls, values):
        """Validate Recorded Date"""
        recorded_date = values["recorded"]
        NHSValidators.validate_recorded_date(recorded_date)
        return values

    # TODO: Can't validate yet as report origin is not in the sample data
    @classmethod
    def validate_report_origin(cls, values):
        """Validate Report Origin"""
        report_origin = values["reportOrigin"]["text"]
        primary_source = values["primarySource"]
        NHSValidators.validate_report_origin(report_origin, primary_source)
        return values

    @classmethod
    def validate_not_given(cls, values):
        """Validate Not Given"""
        not_given = values["status"]
        NHSValidators.validate_not_given(not_given)
        return values

    @classmethod
    def validate_vaccination_procedure_code(cls, values):
        """Validate Vaccination Procedure Code"""
        for record in values["extension"]:
            if (
                record["url"]
                == "https://fhir.hl7.org.uk/StructureDefinition/Extension\
                    -UKCore-VaccinationProcedure"
            ):
                vaccination_procedure_code = record["valueCodeableConcept"]["coding"][
                    0
                ]["code"]

        not_given = values["status"]

        NHSValidators.validate_vaccination_procedure_code(
            vaccination_procedure_code, not_given
        )
        return values

    # TODO: Can't validate yet as vaccination situation code is not in the sample data
    @classmethod
    def validate_vaccination_situation_code(cls, values):
        """Validate Vaccination Procedure Code"""
        for record in values["extension"]:
            if (
                record["url"]
                == "https://fhir.hl7.org.uk/StructureDefinition/Extension\
                    -UKCore-VaccinationSituation"
            ):
                vaccination_situation_code = record["valueCodeableConcept"]["coding"][
                    0
                ]["code"]

        not_given = values["status"]

        NHSValidators.validate_vaccination_procedure_code(
            vaccination_situation_code, not_given
        )
        return values

    # TODO: Can't validate yet as reason not given code is not in the sample data
    @classmethod
    def validate_reason_not_given_code(cls, values):
        """Validate Reason Not Given Code"""
        reason_not_given_code = values["statusReason"]["coding"][0]["code"]
        not_given = values["status"]

        NHSValidators.validate_vaccination_procedure_code(
            reason_not_given_code, not_given
        )
        return values

    @classmethod
    def validate_dose_sequence(cls, values):
        """Validate Dose Sequence"""
        dose_sequence = values["protocolApplied"][0]["doseNumberPositiveInt"]
        not_given = values["status"]
        NHSValidators.validate_dose_sequence(dose_sequence, not_given)
        return values

    @classmethod
    def validate_vaccine_product_code(cls, values):
        """Validate Vaccine Product Code"""
        for record in values["vaccineCode"]["coding"]:
            if record["system"] == "http://snomed.info/sct":
                vaccine_product_code = record["code"]
        not_given = values["status"]
        NHSValidators.validate_vaccine_product_code(vaccine_product_code, not_given)
        return values

    # TODO: Can't validate yet as vaccine manufacturer is not in the sample data
    @classmethod
    def validate_vaccine_manufacturer(cls, values):
        """Validate Vaccine Manufacturer"""
        vaccine_manufacturer = values["manufacturer"]["name"]
        not_given = values["status"]
        NHSValidators.validate_vaccine_manufacturer(vaccine_manufacturer, not_given)
        return values

    @classmethod
    def validate_batch_number(cls, values):
        """Validate Batch Number"""
        batch_number = values["lotNumber"]
        not_given = values["status"]
        NHSValidators.validate_batch_number(batch_number, not_given)
        return values

    @classmethod
    def validate_expiry_date(cls, values):
        """Validate Expiry Date"""
        expiry_date = values["expirationDate"]
        not_given = values["status"]
        NHSValidators.validate_expiry_date(expiry_date, not_given)
        return values

    @classmethod
    def validate_route_of_vaccination_code(cls, values):
        """Validate Route of Vaccination Code"""
        for record in values["route"]["coding"]:
            if record["system"] == "http://snomed.info/sct":
                route_of_vaccination_code = record["code"]
        not_given = values["status"]
        NHSValidators.validate_route_of_vaccination_code(
            route_of_vaccination_code, not_given
        )
        return values

    @classmethod
    def validate_dose_amount(cls, values):
        """Validate Dose Amount"""
        dose_amount = values["doseQuantity"]["value"]
        not_given = values["status"]
        NHSValidators.validate_dose_amount(dose_amount, not_given)
        return values

    @classmethod
    def validate_dose_unit_code(cls, values):
        """Validate Dose Unit Code"""
        dose_unit_code = values["doseQuantity"]["code"]
        not_given = values["status"]
        NHSValidators.validate_dose_unit_code(dose_unit_code, not_given)
        return values

    def validate(self):
        Immunization.add_root_validator(self.validate_nhs_number)
        # Immunization.add_root_validator(self.validate_person_dob)
        # Immunization.add_root_validator(self.validate_gender_code)
        # Immunization.add_root_validator(self.validate_person_postcode)
        Immunization.add_root_validator(self.validate_date_and_time)
        # Immunization.add_root_validator(self.validate_site_code)
        Immunization.add_root_validator(self.validate_action_flag)
        # Immunization.add_root_validator(self.validate_performing_professional_forename)
        Immunization.add_root_validator(
            self.validate_performing_professional_body_reg_code
        )
        Immunization.add_root_validator(self.validate_recorded_date)
        # Immunization.add_root_validator(self.validate_report_origin)
        Immunization.add_root_validator(self.validate_not_given)
        Immunization.add_root_validator(self.validate_vaccination_procedure_code)
        # Immunization.add_root_validator(self.validate_vaccination_situation_code)
        # Immunization.add_root_validator(self.validate_reason_not_given_code)
        Immunization.add_root_validator(self.validate_dose_sequence)
        Immunization.add_root_validator(self.validate_vaccine_product_code)
        # Immunization.add_root_validator(self.validate_vaccine_manufacturer)
        Immunization.add_root_validator(self.validate_batch_number)
        Immunization.add_root_validator(self.validate_expiry_date)
        Immunization.add_root_validator(self.validate_route_of_vaccination_code)
        Immunization.add_root_validator(self.validate_dose_amount)
        Immunization.add_root_validator(self.validate_dose_unit_code)

        immunization = Immunization.parse_obj(self.json_data)
        ic(immunization.dict())
