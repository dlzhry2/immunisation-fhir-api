"""Utils for backend src code"""

from models.obtain_field_value import ObtainFieldValue
from models.field_locations import FieldLocations


def obtain_field_value(imms: dict, field_name: str) -> any:
    """Finds and returns the field value from the imms json data. Returns none if field not found."""

    # Obtain the function for extracting the field value from the json data
    function_for_obtaining_field_value = getattr(ObtainFieldValue, field_name)

    # Obtain the field value, or set it to none if it can't be found
    try:
        field_value = function_for_obtaining_field_value(imms)
    except (KeyError, IndexError, TypeError):
        field_value = None

    return field_value


def obtain_field_location(field_name: str, imms: dict = None) -> str:

    field_locations = FieldLocations()

    # Ensure dynamic fields are set using `imms` data
    field_locations.set_dynamic_fields(imms)

    # print(field_locations.patient_name_given)

    # Check for static fields
    try:
        return getattr(FieldLocations, field_name)  # Static fields are accessed directly via the class
    except AttributeError:
        pass

    # Then check for dynamic fields in the instance
    if field_name in field_locations.__dict__:
        return getattr(field_locations, field_name)
