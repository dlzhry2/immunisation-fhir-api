"""Functions for validating that mandation requirements are met"""

from models.utils.post_validation_utils import MandatoryError
from models.field_locations import FieldLocations
from models.obtain_field_value import ObtainFieldValue


class MandationFunctions:
    """Functions for validating that mandation requirements are met"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def mandatory(imms: dict, field_value, field_location: str, vaccine_type) -> None:
        """Raises MandatoryError if field value is None"""
        if field_value is None:
            raise MandatoryError(f"{field_location} is a mandatory field")

    @staticmethod
    def required(imms: dict, field_value, field_location: str, vaccine_type) -> None:
        """Allows all field values to pass"""

    @staticmethod
    def optional(imms: dict, field_value, field_location: str, vaccine_type) -> None:
        """Allows all field values to pass"""

    @staticmethod
    def mandatory_when_practitioner_identifier_value_present(
        imms: dict, field_value, field_location: str, vaccine_type
    ) -> None:
        """Raises MandatoryError if practitioner_identifier_field is present and given field value is None"""
        try:
            practitioner_identifier_value = getattr(ObtainFieldValue, "practitioner_identifier_value")(imms)
        except (KeyError, IndexError):
            practitioner_identifier_value = None

        practitioner_identifier_value_field_location = getattr(FieldLocations, "practitioner_identifier_value")

        if practitioner_identifier_value is not None and field_value is None:
            raise MandatoryError(
                f"{field_location} is mandatory when {practitioner_identifier_value_field_location} is"
                + f" present and vaccination type is {vaccine_type}"
            )

    @staticmethod
    def mandatory_when_primary_source_is_false(imms: dict, field_value, field_location: str, vaccine_type):
        """Raises MandatoryError if primary_source is false and given field value is None"""
        try:
            primary_source = getattr(ObtainFieldValue, "primary_source")(imms)
        except (KeyError, IndexError):
            primary_source = None

        primary_source_field_location = getattr(FieldLocations, "primary_source")

        if primary_source is False and field_value is None:
            raise MandatoryError(f"{field_location} is mandatory when {primary_source_field_location} is false")
