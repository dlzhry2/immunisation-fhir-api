"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from models.nhs_validators import NHSImmunizationValidators


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def validate_patient_identifier_value(cls, values: dict) -> dict:
        """Validate patient identifier value (NHS number)"""
        if values.get("patient"):
            patient_identifier_value = values.get("patient").identifier.value
            NHSImmunizationValidators.validate_patient_identifier_value(
                patient_identifier_value
            )
        return values

    @classmethod
    def pre_validate_occurrence_date_time(cls, values: dict) -> dict:
        """Pre-validate occurrence date time"""
        occurrence_date_time = values.get("occurrenceDateTime", None)
        if not isinstance(occurrence_date_time, str):
            raise ValueError("occurrenceDateTime must be a string")

        if occurrence_date_time.isnumeric():
            raise ValueError(
                "occurrenceDateTime must be in the format YYYY-MM-DDThh:mm:ss+00:00"
            )

        return values

    @classmethod
    def validate_occurrence_date_time(cls, values: dict) -> dict:
        """Validate occurrence date time"""
        occurrence_date_time = values.get("occurrenceDateTime", None)
        values[
            "occurrenceDateTime"
        ] = NHSImmunizationValidators.validate_occurrence_date_time(
            occurrence_date_time
        )
        return values

    @classmethod
    def validate_questionnaire_site_code_code(cls, values: dict) -> dict:
        """
        Validate questionnaire site code (code of the Commissioned Healthcare Provider who has
        administered the vaccination)
        """
        questionnaire_site_code_code = None
        for record in values.get("contained"):
            if (
                record.resource_type == "QuestionnaireResponse"
                and record.item is not None
            ):
                for item in record.item:
                    if item.linkId == "SiteCode":
                        questionnaire_site_code_code = item.answer[0].valueCoding.code

        NHSImmunizationValidators.validate_questionnaire_site_code_code(
            questionnaire_site_code_code
        )
        return values

    @classmethod
    def validate_identifier_value(cls, values: dict) -> dict:
        """Validate immunization identifier value"""
        identifier_value = values.get("identifier")[0].value
        NHSImmunizationValidators.validate_identifier_value(identifier_value)
        return values

    @classmethod
    def validate_identifier_system(cls, values: dict) -> dict:
        """Validate immunization identifier system"""
        identifier_system = values.get("identifier")[0].system
        NHSImmunizationValidators.validate_identifier_value(identifier_system)
        return values

    @classmethod
    def validate_status(cls, values) -> dict:
        """Validate status (Action Flag)"""
        status = values.get("status")
        NHSImmunizationValidators.validate_status(status)
        return values

    @classmethod
    def validate_recorded(cls, values: dict) -> dict:
        """Validate Recorded (recorded date)"""
        recorded = str(values.get("recorded"))
        NHSImmunizationValidators.validate_recorded(recorded)
        return values

    @classmethod
    def validate_primary_source(cls, values: dict) -> dict:
        """Validate primary source"""
        primary_source = values.get("primarySource")
        NHSImmunizationValidators.validate_primary_source(primary_source)
        return values

    @classmethod
    def validate_report_origin_text(cls, values) -> dict:
        """Validate Report Origin text"""
        report_origin_text = values.get("reportOrigin").text
        primary_source = values.get("primarySource")
        NHSImmunizationValidators.validate_report_origin_text(
            report_origin_text, primary_source
        )
        return values

    @classmethod
    def validate_vaccination_procedure_code(cls, values) -> dict:
        """Validate Vaccination Procedure Code"""
        url = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure"
        for record in values.get("extension"):
            if record.url == url:
                vaccination_procedure_code = record.valueCodeableConcept.coding[0].code
        not_given = values.get("status")

        NHSImmunizationValidators.validate_vaccination_procedure_code(
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

        NHSImmunizationValidators.validate_vaccination_procedure_code(
            vaccination_situation_code, not_given
        )
        return values

    @classmethod
    def validate_reason_not_given_code(cls, values) -> dict:
        """Validate Reason Not Given Code"""
        reason_not_given_code = values.get("statusReason").coding[0].code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_vaccination_procedure_code(
            reason_not_given_code, not_given
        )
        return values

    @classmethod
    def validate_dose_sequence(cls, values) -> dict:
        """Validate Dose Sequence"""
        dose_sequence = values.get("protocolApplied")[0].doseNumberPositiveInt
        not_given = values.get("status")
        NHSImmunizationValidators.validate_dose_sequence(dose_sequence, not_given)
        return values

    @classmethod
    def validate_vaccine_product_code(cls, values) -> dict:
        """Validate Vaccine Product Code"""
        for record in values.get("vaccineCode").coding:
            if record.system == "http://snomed.info/sct":
                vaccine_product_code = record.code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_vaccine_product_code(
            vaccine_product_code, not_given
        )
        return values

    @classmethod
    def validate_vaccine_manufacturer(cls, values) -> dict:
        """Validate Vaccine Manufacturer"""
        vaccine_manufacturer = values.get("manufacturer").display
        not_given = values.get("status")
        NHSImmunizationValidators.validate_vaccine_manufacturer(
            vaccine_manufacturer, not_given
        )
        return values

    @classmethod
    def validate_batch_number(cls, values) -> dict:
        """Validate Batch Number"""
        batch_number = values.get("lotNumber")
        not_given = values.get("status")
        NHSImmunizationValidators.validate_batch_number(batch_number, not_given)
        return values

    @classmethod
    def validate_expiry_date(cls, values) -> dict:
        """Validate Expiry Date"""
        expiry_date = str(values.get("expirationDate"))
        not_given = values.get("status")
        NHSImmunizationValidators.validate_expiry_date(expiry_date, not_given)
        return values

    @classmethod
    def validate_route_of_vaccination_code(cls, values) -> dict:
        """Validate Route of Vaccination Code"""
        for record in values.get("route").coding:
            if record.system == "http://snomed.info/sct":
                route_of_vaccination_code = record.code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_route_of_vaccination_code(
            route_of_vaccination_code, not_given
        )
        return values

    @classmethod
    def validate_dose_amount(cls, values) -> dict:
        """Validate Dose Amount"""
        dose_amount = values.get("doseQuantity").value
        not_given = values.get("status")
        NHSImmunizationValidators.validate_dose_amount(str(dose_amount), not_given)
        return values

    @classmethod
    def validate_dose_unit_code(cls, values) -> dict:
        """Validate Dose Unit Code"""
        dose_unit_code = values.get("doseQuantity").code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_dose_unit_code(dose_unit_code, not_given)
        return values

    @classmethod
    def validate_indication_code(cls, values) -> dict:
        """Validate Indication Code"""
        indication_code = values.get("reasonCode")[0].coding[0].code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_indication_code(indication_code, not_given)
        return values

    @classmethod
    def validate_consent_for_treatment_code(cls, values) -> dict:
        """Validate Consent for Treatment Code"""
        for record in values.get("contained")[0].item:
            if record.linkId == "Consent":
                consent_for_treatment_code = record.answer[0].valueCoding.code
        not_given = values.get("status")
        NHSImmunizationValidators.validate_consent_for_treatment_code(
            consent_for_treatment_code, not_given
        )
        return values

    @classmethod
    def validate_submitted_timestamp(cls, values) -> dict:
        """Validate Submitted Timestamp"""
        for record in values.get("contained")[0].item:
            if record.linkId == "SubmittedTimeStamp":
                submitted_timestamp = record.answer[0].valueCoding.code
        NHSImmunizationValidators.validate_submitted_timestamp(submitted_timestamp)
        return values

    @classmethod
    def validate_location_code(cls, values) -> dict:
        """Validate Location Code"""
        location_code = values.get("location").identifier.value
        NHSImmunizationValidators.validate_location_code(location_code)
        return values

    @classmethod
    def validate_reduce_validation_code(cls, values) -> dict:
        """Validate Reduce Validation Code"""
        for record in values.get("contained")[0].item:
            if record.linkId == "ReduceValidation":
                reduce_validation_code = record.answer[0].valueCoding.code
                reduce_validation_reason = record.answer[0].valueCoding.display
        NHSImmunizationValidators.validate_reduce_validation_code(
            reduce_validation_code, reduce_validation_reason
        )
        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Immunization.add_root_validator(self.validate_patient_identifier_value)
        Immunization.add_root_validator(
            self.pre_validate_occurrence_date_time, pre=True
        )
        Immunization.add_root_validator(self.validate_occurrence_date_time)
        Immunization.add_root_validator(self.validate_questionnaire_site_code_code)
        Immunization.add_root_validator(self.validate_identifier_value)
        Immunization.add_root_validator(self.validate_identifier_system)
        Immunization.add_root_validator(self.validate_status)
        Immunization.add_root_validator(self.validate_recorded)
        Immunization.add_root_validator(self.validate_primary_source)
        Immunization.add_root_validator(self.validate_report_origin_text)
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

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        immunization = Immunization.parse_obj(json_data)
        return immunization
