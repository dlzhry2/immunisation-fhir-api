"""Immunization FHIR R4B validator"""
import json
from typing import Literal
from fhir.resources.R4B.immunization import Immunization
from models.fhir_immunization_pre_validators import PreValidators
from models.fhir_immunization_post_validators import FHIRImmunizationPostValidators
from models.utils.generic_utils import get_generic_questionnaire_response_value
from pydantic import ValidationError


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self, add_post_validators: bool = True, immunization: Immunization = None) -> None:
        self.immunization = immunization
        self.reduce_validation_code = False
        self.add_post_validators = add_post_validators
        self.pre_validators = None
        
    def initialize_immunization(self, json_data):
        self.immunization = Immunization.parse_obj(json_data)
        
    def initialize_pre_validators(self, immunization):
        """Initialize pre validators with data."""
        self.pre_validators = PreValidators(immunization)
        
    def add_custom_root_pre_validators(self):
        """
        Run custom pre validators to the data.
        """
        error = self.pre_validators.validate()
        if error:
            raise ValueError(error)

    def set_reduce_validation_code(self, json_data):
        """Set the reduce validation code"""
        reduce_validation_code = False

        # If reduce_validation_code field exists then retrieve it's value
        try:
            reduce_validation_code = get_generic_questionnaire_response_value(
                json_data, "ReduceValidation", "valueBoolean"
            )
        except (KeyError, IndexError, AttributeError, TypeError):
            pass
        finally:
            # If no value is given, then ReduceValidation default value is False
            if reduce_validation_code is None:
                reduce_validation_code = False

        self.reduce_validation_code = reduce_validation_code

    def add_custom_root_post_validators(self):
        """
        Add custom NHS post validators to the model

        NOTE: THE ORDER IN WHICH THE VALIDATORS ARE ADDED IS IMPORTANT! DO NOT CHANGE THE ORDER
        WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST.
        """
        skip_on_failure = True
        # DO NOT CHANGE THE ORDER WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST
        if not hasattr(self.immunization, "validate_and_set_vaccination_procedure_code"):
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_and_set_vaccination_procedure_code,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.set_status,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_identifier_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_name_given,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_name_family,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_birth_date,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_gender,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_patient_address_postal_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_occurrence_date_time,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_organization_identifier_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_organization_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_identifier_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_identifier_system,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_practitioner_name_given,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_practitioner_name_family,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_practitioner_identifier_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_practitioner_identifier_system,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_performer_sds_job_role,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_recorded,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_primary_source,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_report_origin_text,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_vaccination_procedure_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_vaccination_situation_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_vaccination_situation_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_status_reason_coding_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_status_reason_coding_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_protocol_applied_dose_number_positive_int,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_vaccine_code_coding_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_vaccine_code_coding_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_manufacturer_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_lot_number,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_expiration_date,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_site_coding_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_site_coding_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_route_coding_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_route_coding_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_dose_quantity_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_dose_quantity_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_dose_quantity_unit,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_reason_code_coding_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_reason_code_coding_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_nhs_number_verification_status_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_nhs_number_verification_status_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_organization_identifier_system,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_local_patient_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_local_patient_system,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_consent_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_consent_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_care_setting_code,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_care_setting_display,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_ip_address,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_user_id,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_user_name,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_user_email,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_submitted_time_stamp,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_location_identifier_value,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_location_identifier_system,
                skip_on_failure=skip_on_failure,
            )
            self.immunization.add_root_validator(
                FHIRImmunizationPostValidators.validate_reduce_validation_reason,
                skip_on_failure=skip_on_failure,
            )

    def remove_custom_root_validators(self, mode: Literal["pre", "post"]):
        """Remove custom NHS validators from the model"""
        if mode == "pre":
            for validator in self.immunization.__pre_root_validators__:
                if "FHIRImmunizationPreValidators" in str(validator):
                    self.immunization.__pre_root_validators__.remove(validator)
        elif mode == "post":
            for validator in self.immunization.__post_root_validators__:
                if "FHIRImmunizationPostValidators" in str(validator):
                    self.immunization.__post_root_validators__.remove(validator)

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        self.set_reduce_validation_code(json_data)
        self.initialize_pre_validators(json_data)

        try:
            self.add_custom_root_pre_validators()
        except Exception as e:
            raise e
        
        self.initialize_immunization(json_data)

        if self.add_post_validators and not self.reduce_validation_code:
            self.add_custom_root_post_validators() 

        return self.immunization
