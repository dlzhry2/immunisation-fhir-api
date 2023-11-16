"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from models.nhs_validators import NHSValidators


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self, json_data) -> None:
        self.json_data = json_data

    @classmethod
    def validate_nhs_number(cls, values: dict) -> dict:
        """Validate NHS Number"""
        nhs_number = values.get("patient").identifier.value
        NHSValidators.validate_nhs_number(nhs_number)
        return values

    @classmethod
    def validate_date_and_time(cls, values: dict) -> dict:
        """Validate Date and Time"""
        milli_secs = values.get("occurrenceDateTime").strftime("%z")
        milli_secs = milli_secs[:3] + ":" + milli_secs[3:]
        date_and_time = (
            f"{values['occurrenceDateTime'].strftime('%Y-%m-%dT%H:%M:%S')}{milli_secs}"
        )
        NHSValidators.validate_date_and_time(date_and_time)
        return values

    @classmethod
    def validate_site_code(cls, values: dict) -> dict:
        """Validate Site Code"""
        site_code = values.get("location").identifier.value
        NHSValidators.validate_site_code(site_code)
        return values

    @classmethod
    def validate_action_flag(cls, values) -> dict:
        """Validate Action Flag"""
        action_flag = values.get("status")
        NHSValidators.validate_action_flag(action_flag)
        return values

    @classmethod
    def validate_recorded_date(cls, values: dict) -> dict:
        """Validate Recorded Date"""
        recorded_date = str(values.get("recorded"))
        NHSValidators.validate_recorded_date(recorded_date)
        return values

    @classmethod
    def validate_report_origin(cls, values) -> dict:
        """Validate Report Origin"""
        report_origin = values.get("reportOrigin").text
        primary_source = values.get("primarySource")
        NHSValidators.validate_report_origin(report_origin, primary_source)
        return values

    @classmethod
    def validate_vaccination_procedure_code(cls, values) -> dict:
        """Validate Vaccination Procedure Code"""
        url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure"
        for record in values.get("extension"):
            if record.url == url:
                vaccination_procedure_code = record.valueCodeableConcept.coding[0].code
        not_given = values.get("status")

        NHSValidators.validate_vaccination_procedure_code(
            vaccination_procedure_code, not_given
        )
        return values

    @classmethod
    def validate_vaccination_situation_code(cls, values) -> dict:
        """Validate Vaccination Procedure Code"""
        url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation"
        for record in values.get("extension"):
            if record.url == url:
                vaccination_situation_code = record.valueCodeableConcept.coding[0].code
        not_given = values.get("status")

        NHSValidators.validate_vaccination_procedure_code(
            vaccination_situation_code, not_given
        )
        return values

    @classmethod
    def validate_reason_not_given_code(cls, values) -> dict:
        """Validate Reason Not Given Code"""
        reason_not_given_code = values.get("statusReason").coding[0].code
        not_given = values.get("status")
        NHSValidators.validate_vaccination_procedure_code(
            reason_not_given_code, not_given
        )
        return values

    @classmethod
    def validate_dose_sequence(cls, values) -> dict:
        """Validate Dose Sequence"""
        dose_sequence = values.get("protocolApplied")[0].doseNumberPositiveInt
        not_given = values.get("status")
        NHSValidators.validate_dose_sequence(dose_sequence, not_given)
        return values

    @classmethod
    def validate_vaccine_product_code(cls, values) -> dict:
        """Validate Vaccine Product Code"""
        for record in values.get("vaccineCode").coding:
            if record.system == "http://snomed.info/sct":
                vaccine_product_code = record.code
        not_given = values.get("status")
        NHSValidators.validate_vaccine_product_code(vaccine_product_code, not_given)
        return values

    @classmethod
    def validate_vaccine_manufacturer(cls, values) -> dict:
        """Validate Vaccine Manufacturer"""
        vaccine_manufacturer = values.get("manufacturer").display
        not_given = values.get("status")
        NHSValidators.validate_vaccine_manufacturer(vaccine_manufacturer, not_given)
        return values

    @classmethod
    def validate_batch_number(cls, values) -> dict:
        """Validate Batch Number"""
        batch_number = values.get("lotNumber")
        not_given = values.get("status")
        NHSValidators.validate_batch_number(batch_number, not_given)
        return values

    @classmethod
    def validate_expiry_date(cls, values) -> dict:
        """Validate Expiry Date"""
        expiry_date = str(values.get("expirationDate"))
        not_given = values.get("status")
        NHSValidators.validate_expiry_date(expiry_date, not_given)
        return values

    @classmethod
    def validate_route_of_vaccination_code(cls, values) -> dict:
        """Validate Route of Vaccination Code"""
        for record in values.get("route").coding:
            if record.system == "http://snomed.info/sct":
                route_of_vaccination_code = record.code
        not_given = values.get("status")
        NHSValidators.validate_route_of_vaccination_code(
            route_of_vaccination_code, not_given
        )
        return values

    @classmethod
    def validate_dose_amount(cls, values) -> dict:
        """Validate Dose Amount"""
        dose_amount = values.get("doseQuantity").value
        not_given = values.get("status")
        NHSValidators.validate_dose_amount(str(dose_amount), not_given)
        return values

    @classmethod
    def validate_dose_unit_code(cls, values) -> dict:
        """Validate Dose Unit Code"""
        dose_unit_code = values.get("doseQuantity").code
        not_given = values.get("status")
        NHSValidators.validate_dose_unit_code(dose_unit_code, not_given)
        return values

    @classmethod
    def validate_indication_code(cls, values) -> dict:
        """Validate Indication Code"""
        indication_code = values.get("reasonCode")[0].coding[0].code
        not_given = values.get("status")
        NHSValidators.validate_indication_code(indication_code, not_given)
        return values

    @classmethod
    def validate_consent_for_treatment_code(cls, values) -> dict:
        """Validate Consent for Treatment Code"""
        for record in values.get("contained")[0].item:
            if record.linkId == "Consent":
                consent_for_treatment_code = record.answer[0].valueCoding.code
        not_given = values.get("status")
        NHSValidators.validate_consent_for_treatment_code(
            consent_for_treatment_code, not_given
        )
        return values

    @classmethod
    def validate_submitted_timestamp(cls, values) -> dict:
        """Validate Submitted Timestamp"""
        for record in values.get("contained")[0].item:
            if record.linkId == "SubmittedTimeStamp":
                submitted_timestamp = record.answer[0].valueCoding.code
        NHSValidators.validate_submitted_timestamp(submitted_timestamp)
        return values

    @classmethod
    def validate_location_code(cls, values) -> dict:
        """Validate Location Code"""
        location_code = values.get("location").identifier.value
        NHSValidators.validate_location_code(location_code)
        return values

    @classmethod
    def validate_reduce_validation_code(cls, values) -> dict:
        """Validate Reduce Validation Code"""
        for record in values.get("contained")[0].item:
            if record.linkId == "ReduceValidation":
                reduce_validation_code = record.answer[0].valueCoding.code
                reduce_validation_reason = record.answer[0].valueCoding.display
        NHSValidators.validate_reduce_validation_code(
            reduce_validation_code, reduce_validation_reason
        )
        return values

    def validate(self) -> Immunization:
        """
        Add custom NHS validators to the Immunization model then generate the Immunization model
        from the JSON data
        """
        # Custom NHS validators
        Immunization.add_root_validator(self.validate_nhs_number)
        Immunization.add_root_validator(self.validate_date_and_time)
        Immunization.add_root_validator(self.validate_site_code)
        Immunization.add_root_validator(self.validate_action_flag)
        Immunization.add_root_validator(self.validate_recorded_date)
        Immunization.add_root_validator(self.validate_report_origin)
        Immunization.add_root_validator(self.validate_vaccination_procedure_code)
        Immunization.add_root_validator(self.validate_vaccination_situation_code)
        Immunization.add_root_validator(self.validate_reason_not_given_code)
        Immunization.add_root_validator(self.validate_dose_sequence)
        Immunization.add_root_validator(self.validate_vaccine_product_code)
        Immunization.add_root_validator(self.validate_vaccine_manufacturer)
        Immunization.add_root_validator(self.validate_batch_number)
        Immunization.add_root_validator(self.validate_expiry_date)
        Immunization.add_root_validator(self.validate_route_of_vaccination_code)
        Immunization.add_root_validator(self.validate_dose_amount)
        Immunization.add_root_validator(self.validate_dose_unit_code)
        Immunization.add_root_validator(self.validate_indication_code)
        Immunization.add_root_validator(self.validate_consent_for_treatment_code)
        Immunization.add_root_validator(self.validate_submitted_timestamp)
        Immunization.add_root_validator(self.validate_location_code)
        Immunization.add_root_validator(self.validate_reduce_validation_code)

        # Generate the Immunization model from the JSON data
        immunization = Immunization.parse_obj(self.json_data)

        return immunization
