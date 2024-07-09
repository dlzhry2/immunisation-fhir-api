"""Immunization FHIR R4B validator"""

from fhir.resources.R4B.immunization import Immunization
from models.fhir_immunization_pre_validators import PreValidators
from models.fhir_immunization_post_validators import PostValidators


class ImmunizationValidator:
    """
    Validate the FHIR Immunization Resource JSON data against the NHS specific validators
    and Immunization FHIR profile
    """

    def __init__(self, add_post_validators: bool = True) -> None:
        self.reduce_validation_code: bool
        self.add_post_validators = add_post_validators

    @staticmethod
    def run_pre_validators(immunization: dict) -> None:
        """Run pre validation on the FHIR Immunization Resource JSON data"""
        error = PreValidators(immunization).validate()
        if error:
            raise ValueError(error)

    def run_fhir_validators(self, immunization: dict) -> None:
        """Run the FHIR validator on the FHIR Immunization Resource JSON data"""
        Immunization.parse_obj(immunization)

    @staticmethod
    def run_post_validators(immunization: dict) -> None:
        """Run post validation on the FHIR Immunization Resource JSON data"""
        error = PostValidators(immunization).validate()
        if error:
            raise ValueError(error)

    # TODO: Update this as reduce_validation_code is no longer found in the payload after data minimisation
    def set_reduce_validation_code(self):
        """Set the reduce validation code (default to false if no reduceValidation code is given)"""
        self.reduce_validation_code = False

    def validate(self, immunization_json_data: dict) -> Immunization:
        """Generate the Immunization model"""
        self.set_reduce_validation_code()

        # Pre-FHIR validations
        try:
            self.run_pre_validators(immunization_json_data)
        except Exception as e:
            raise e

        # FHIR validations
        self.run_fhir_validators(immunization_json_data)

        # Post-FHIR validations
        if self.add_post_validators and not self.reduce_validation_code:
            try:
                self.run_post_validators(immunization_json_data)
            except Exception as e:
                raise e

        return immunization_json_data
