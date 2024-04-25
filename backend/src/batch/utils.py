from datetime import datetime
from decimal import Decimal, InvalidOperation


def _is_not_empty(value: any) -> bool:
    """Determine if a value is not empty i.e. there is data present. Note that some
    "Falsey" values, such as zero values and a boolean of false, are valid data"""
    return value not in [None, "", [], {}, (), [""]]


def _add_questionnaire_item_to_list(items: list, linkId: str, item: dict):
    # TODO: Need to unit test this function
    items.append({"linkId": linkId, "answer": [item]})


class Create:

    @staticmethod
    def dict(fields: dict) -> dict:
        """Makes a dictionary with all empty items removed"""
        dictionary = {}
        for fhir_key_name, field_value in fields.items():
            if _is_not_empty(field_value):
                dictionary[fhir_key_name] = field_value
        return dictionary

    @staticmethod
    def extension_item(url: str, system: str, code: str, display: str) -> dict:
        return {
            "url": url,
            "valueCodeableConcept": {"coding": [{"system": system, "code": code, "display": display}]},
        }


class Add:

    @staticmethod
    def item(dictionary: dict, fhir_field_name: str, value: any, conversion_fn=None):
        if _is_not_empty(value):
            dictionary[fhir_field_name] = value if conversion_fn is None else conversion_fn(value)

    @staticmethod
    def dict(dictionary: dict, fhir_field_name: str, fields: dict):
        if any(_is_not_empty(field_value) for field_value in fields.values()):
            Add.item(dictionary, fhir_field_name, Create.dict(fields))

    @staticmethod
    def list_of_dict(dictionary: dict, fhir_field_name: str, fields: dict):
        if any(_is_not_empty(field_value) for field_value in fields.values()):
            Add.item(dictionary, fhir_field_name, [Create.dict(fields)])

    @staticmethod
    def custom_item(dictionary: dict, fhir_field_name: str, field_values: list, item_to_add: any):
        if any(_is_not_empty(field_value) for field_value in field_values):
            dictionary[fhir_field_name] = item_to_add

    @staticmethod
    def snomed(dictionary: dict, fhir_field_name: str, code: str, display: str):
        if _is_not_empty(code) or _is_not_empty(display):
            dictionary[fhir_field_name] = {
                "coding": [Create.dict({"system": "http://snomed.info/sct", "code": code, "display": display})]
            }


class Convert:
    """
    Some values need to be converted when the batch input is transformed into FHIR Immunization Resources. Each of the
    conversion functions returns the converted value where possible, or returns the originial value otherwise
    """

    @staticmethod
    def date_time(date_time: str) -> str:
        try:
            parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S00")
        except ValueError:
            parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S")
        try:
            return parsed_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        except ValueError:
            return date_time

    @staticmethod
    def date(date: str) -> str:
        try:
            return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            return date

    @staticmethod
    def gender_code(code: str) -> str:
        """Converts code to fhir gender, or returns the original code if it is not recognized"""
        code_to_fhir = {"1": "male", "2": "female", "9": "other", "0": "unknown"}
        return code_to_fhir.get(code, code)

    @staticmethod
    def boolean(value: str) -> bool:
        """Booleans are represented as strings in the CSV. This function converts them to Python booleans where possible"""
        lower_value = value.lower() if isinstance(value, str) else None
        return {"true": True, "false": False}.get(lower_value, value)

    @staticmethod
    def decimal(value: str) -> any:
        try:
            return Decimal(value)
        except (TypeError, InvalidOperation):
            return value

    @staticmethod
    def integer(value: str) -> any:
        try:
            return int(value)
        except (TypeError, ValueError):
            return value

    @staticmethod
    def to_lower(value: str) -> any:
        try:
            return value.lower()
        except (AttributeError, SyntaxError):
            return value
