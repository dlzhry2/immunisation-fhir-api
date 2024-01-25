"""Immunization FHIR R4B validator"""
from typing import Literal
from fhir.resources.R4B.immunization import Immunization
from models.fhir_immunization_pre_validators import FHIRImmunizationPreValidators
from models.fhir_immunization_post_validators import FHIRImmunizationPostValidators


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self) -> None:
        class NewImmunization(Immunization):
            """
            Workaround for tests so we can instantiate our own instance of Immunization, and add
            the pre/post validators independently without affecting other tests
            """

        self.immunization = NewImmunization

    def add_custom_root_pre_validators(self):
        """
        Add custom NHS validators to the model

        NOTE: THE ORDER IN WHICH THE VALIDATORS ARE ADDED IS IMPORTANT! DO NOT CHANGE THE ORDER
        WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST.
        """
        # DO NOT CHANGE THE ORDER WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST

        self.immunization.add_root_validator(
            FHIRImmunizationPreValidators.pre_validate_contained, pre=True
        )

        self.immunization.add_root_validator(
            FHIRImmunizationPreValidators.pre_validate_patient_identifier, pre=True
        )

        self.immunization.add_root_validator(
            FHIRImmunizationPreValidators.pre_validate_patient_identifier_value,
            pre=True,
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPreValidators.pre_validate_occurrence_date_time, pre=True
        )

        self.immunization.add_root_validator(
            FHIRImmunizationPreValidators.pre_validate_questionnaire_response_item,
            pre=True,
        )

        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_questionnaire_answers, pre=True
        # )

        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_questionnaire_site_code_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_site_name_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_identifier, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_identifier_value, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_identifier_system, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_status, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_recorded, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_primary_source, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_report_origin_text, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_extension_value_codeable_concept_codings,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccination_procedure_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccination_procedure_display,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccination_situation_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccination_situation_display,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_status_reason_coding, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_status_reason_coding_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_status_reason_coding_display,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_protocol_applied, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_protocol_applied_dose_number_positive_int,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccine_code_coding, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccine_code_coding_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_vaccine_code_coding_display,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_manufacturer_display, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_lot_number, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_expiration_date, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_site_coding, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_site_coding_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_site_coding_display, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_route_coding, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_route_coding_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_route_coding_display, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_dose_quantity_value, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_dose_quantity_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_dose_quantity_unit, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_reason_code_codings, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_reason_code_coding_codes,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_reason_code_coding_displays,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_nhs_number_status_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_nhs_number_status_display,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_site_code_system, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_local_patient_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_local_patient_system, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_consent_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_consent_display, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_care_setting_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_care_setting_display, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_ip_address_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_user_id_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_user_name_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_user_email_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_submitted_time_stamp_code,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_location_identifier_value,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_location_identifier_system,
        #    pre=True,
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_reduce_validation_code, pre=True
        # )
        # self.immunization.add_root_validator(
        #    FHIRImmunizationPreValidators.pre_validate_reduce_validation_display,
        #    pre=True,
        # )

    def add_custom_root_post_validators(self):
        """
        Add custom NHS post validators to the model

        NOTE: THE ORDER IN WHICH THE VALIDATORS ARE ADDED IS IMPORTANT! DO NOT CHANGE THE ORDER
        WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST.
        """
        # DO NOT CHANGE THE ORDER WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST

        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.set_reduce_validation_code
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_vaccination_procedure_code
        )
        self.immunization.add_root_validator(FHIRImmunizationPostValidators.set_status)
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_patient_identifier_value
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_occurrence_date_time
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_site_code_code
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_site_name_code
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_identifier_value
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_identifier_system
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_recorded
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_primary_source
        )
        self.immunization.add_root_validator(
            FHIRImmunizationPostValidators.validate_report_origin_text
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
        immunization = self.immunization.parse_obj(json_data)
        return immunization
