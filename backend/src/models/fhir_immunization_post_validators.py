"FHIR Immunization Post Validators"

from models.utils.generic_utils import get_target_disease_codes
from models.utils.validation_utils import disease_codes_to_vaccine_type
from models.utils.post_validation_utils import MandatoryError
from models.field_locations import FieldLocations
from models.obtain_field_value import ObtainFieldValue
from models.validation_sets import ValidationSets
from models.mandation_functions import MandationFunctions
from base_utils.base_utils import obtain_field_value, obtain_field_location


class PostValidators:
    """FHIR Immunization Post Validators"""

    def __init__(self, imms):
        self.imms = imms
        self.vaccine_type: str
        self.errors = []

        # Note that the majority of fields require standard validation. Exceptions not included in the below list are
        # vaccine_type, reason_code_coding_code and reason_code_coding_field (these have their own bespoke validation
        # functions). Status is mandatory in FHIR, so there is no post-validation for status as it is handled by the
        # FHIR validator.
        self.fields_with_standard_validation = [
            "occurrence_date_time",
            "patient_identifier_value",
            "patient_name_given",
            "patient_name_family",
            "patient_birth_date",
            "patient_gender",
            "patient_address_postal_code",
            "organization_identifier_value",
            "organization_display",
            "identifier_value",
            "identifier_system",
            "practitioner_name_given",
            "practitioner_name_family",
            "practitioner_identifier_value",
            "practitioner_identifier_system",
            "recorded",
            "primary_source",
            "report_origin_text",
            "vaccination_procedure_code",
            "vaccination_procedure_display",
            "dose_number_positive_int",
            "vaccine_code_coding_code",
            "vaccine_code_coding_display",
            "manufacturer_display",
            "lot_number",
            "expiration_date",
            "site_coding_code",
            "site_coding_display",
            "route_coding_code",
            "route_coding_display",
            "dose_quantity_value",
            "dose_quantity_code",
            "dose_quantity_unit",
            "nhs_number_verification_status_code",
            "nhs_number_verification_status_display",
            "organization_identifier_system",
            "location_identifier_value",
            "location_identifier_system",
        ]

    def run_field_validation(
        self,
        mandation_functions: MandationFunctions,
        validation_set: dict,
        field_name: str,
        field_location: str,
        field_value: any,
    ) -> None:
        """Ascertains the correct mandation rule from the given validation set and applies the validation"""

        # Determine the mandation rule to be followed
        mandation_rule = validation_set[field_name]

        # Obtain the relevant mandation function to apply the mandation rule
        mandation_function = getattr(mandation_functions, mandation_rule)

        # Run the mandation function
        try:
            mandation_function(field_value=field_value, field_location=field_location)

        # Capture any validation errors in self.errors
        except MandatoryError as e:
            self.errors.append(str(e))

    def validate_field(self, mandation_functions: MandationFunctions, validation_set: dict, field_name: str) -> None:
        """Runs standard validation for the field"""

        field_location = obtain_field_location(field_name)
        field_value = obtain_field_value(self.imms, field_name)
        self.run_field_validation(mandation_functions, validation_set, field_name, field_location, field_value)

    def validate_reason_code_coding_field(self, mandation_functions, validation_set, field_type):
        """
        Runs standard validation for each instance of reason_code_coding_{field_type} (note that, because reason_code
        is a list, there may be multiple instances of reason_code_coding_{field_type}, hence the need to iterate).
        """

        # Identify the number of elements of reason_code for validation to inform the number of times to iterate.
        # If there are no elements then set number of iterations to 1 as validation must be run at least once.
        number_of_iterations = len(self.imms["reasonCode"]) if self.imms["reasonCode"] else 1

        # Validate the field for each element of reason_code
        for index in range(number_of_iterations):

            field_name = f"reason_code_coding_{field_type}"
            field_location = f"reasonCode[{index}].coding[0].{field_type}"

            # Obtain the field value from the imms json data, or set it to None if the value can't be found
            try:
                field_value = getattr(ObtainFieldValue, f"reason_code_coding_{field_type}")(self.imms, index)
            except (KeyError, IndexError):
                field_value = None

            self.run_field_validation(mandation_functions, validation_set, field_name, field_location, field_value)

    def validate_and_set_vaccine_type(self, imms: dict) -> dict:
        """
        Validates that the combination of targetDisease codes maps to a valid vaccine type.
        Sets the vaccine type accordingly.
        """
        try:
            # Obtain list of target_disease_codes
            target_disease_codes = get_target_disease_codes(imms)

            # Use the list of target_disease_codes to ascertain the vaccine type
            # Note that disease_codes_to_vaccine_type will raise a value error if the combination of codes is invalid
            if target_disease_codes:
                self.vaccine_type = disease_codes_to_vaccine_type(target_disease_codes)
            # If no target_disease_codes are found then raise an error
            else:
                raise MandatoryError

        # If no target_disease_codes were found then raise a Mandatory error
        except (KeyError, IndexError, TypeError, MandatoryError) as error:
            field_location = getattr(FieldLocations, "target_disease_codes")
            raise MandatoryError(f"{field_location} is a mandatory field") from error

    def validate(self):
        """Run all post-validation checks."""

        # Vaccine_type is a critical validation that other validations rely on, so if it fails an error is raised
        # immediately and no further validation is performed
        try:
            self.validate_and_set_vaccine_type(self.imms)
        except (ValueError, TypeError, IndexError, AttributeError, MandatoryError) as e:
            raise ValueError(str(e)) from e

        # Initialise the mandation validation functions
        mandation_functions = MandationFunctions(self.imms, self.vaccine_type)

        # Obtain the relevant validation set based on the vaccine type
        validation_set = getattr(ValidationSets, self.vaccine_type.lower())

        # Validate all fields which have standard validation
        for field_name in self.fields_with_standard_validation:
            self.validate_field(mandation_functions, validation_set, field_name)

        # Validate reason_code_coding fields. Note that there may be multiple of each of these
        # - all instances of the field will be validated by the validate_reason_code_coding_field validator
        self.validate_reason_code_coding_field(mandation_functions, validation_set, "code")
        self.validate_reason_code_coding_field(mandation_functions, validation_set, "display")

        # Raise any errors
        if self.errors:
            all_errors = "; ".join(self.errors)
            raise ValueError(all_errors)
