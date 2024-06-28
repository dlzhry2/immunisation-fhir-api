"""Functions for validating that mandation requirements are met"""

from dataclasses import dataclass

from models.utils.post_validation_utils import MandatoryError
from models.field_locations import FieldLocations
from base_utils.base_utils import obtain_field_value


@dataclass
class MandationRules:
    """Class containing all the mandation rules, which have corresponding mandation functions"""

    mandatory = "mandatory"
    required = "required"
    optional = "optional"
    mandatory_when_practitioner_identifier_value_present = "mandatory_when_practitioner_identifier_value_present"
    mandatory_when_primary_source_is_false = "mandatory_when_primary_source_is_false"


class MandationFunctions:
    """
    Class containing functions for validating that mandation rules are met.
    Each instance of the class must be initialised with the FHIR Immunization resource JSON data, and the vaccine type.
    Each mandation function takes the field_value and field_location as arguments and raises an error if the field_value
    does not comply with the mandation rule.
    """

    def __init__(self, imms: dict, vaccine_type: str) -> None:
        self.imms = imms
        self.vaccine_type = vaccine_type

    def mandatory(self, field_value, field_location: str) -> None:
        """Raises MandatoryError if field value is None"""
        if field_value is None:
            raise MandatoryError(f"{field_location} is a mandatory field")

    def required(self, field_value, field_location: str) -> None:
        """Allows all field values to pass"""

    def optional(self, field_value, field_location: str) -> None:
        """Allows all field values to pass"""

    def mandatory_when_practitioner_identifier_value_present(self, field_value, field_location: str) -> None:
        """Raises MandatoryError if practitioner_identifier_field is present and given field value is None"""

        practitioner_identifier_value = obtain_field_value(self.imms, "practitioner_identifier_value")
        practitioner_identifier_value_field_location = getattr(FieldLocations, "practitioner_identifier_value")

        if practitioner_identifier_value is not None and field_value is None:
            raise MandatoryError(
                f"{field_location} is mandatory when {practitioner_identifier_value_field_location} is"
                + f" present and vaccination type is {self.vaccine_type}"
            )

    def mandatory_when_primary_source_is_false(self, field_value, field_location: str) -> None:
        """Raises MandatoryError if primary_source is false and given field value is None"""

        primary_source = obtain_field_value(self.imms, "primary_source")
        primary_source_field_location = getattr(FieldLocations, "primary_source")

        if primary_source is False and field_value is None:
            raise MandatoryError(f"{field_location} is mandatory when {primary_source_field_location} is false")
