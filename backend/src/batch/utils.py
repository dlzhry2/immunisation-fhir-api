"""Utils for the batch decorators"""

from datetime import datetime
from decimal import Decimal, InvalidOperation

# TODO: Unit test all functions


def _is_not_empty(value: any) -> bool:
    """
    Determine if a value is not empty i.e. there is data present. Note that some "Falsey" values, such as zero
    values and a boolean of false, are valid data and are therefore classed here as non-empty
    """
    return value not in [None, "", [], {}, (), [""]]


def _add_questionnaire_item_to_list(items: list, link_id: str, item: dict):
    """Adds a questionnaire item to the items list"""
    items.append({"linkId": link_id, "answer": [item]})


class Create:
    """Each function creates an element with empty items removed"""

    @staticmethod
    def dictionary(dictionary: dict) -> dict:
        """Creates a dictionary with all empty items removed"""
        new_dict = {}
        for k, v in dictionary.items():
            if _is_not_empty(v):
                new_dict[k] = v
        return new_dict

    @staticmethod
    def extension_item(url: str, system: str, code: str, display: str) -> dictionary:
        """Creates an extension item using only the non-empty items"""
        extension_item = {"url": url, "valueCodeableConcept": {}}

        Add.list_of_dict(
            extension_item["valueCodeableConcept"], "coding", {"system": system, "code": code, "display": display}
        )

        return extension_item


class Add:
    """Each function adds an element to a dictionary after removing any empty values"""

    @staticmethod
    def item(dictionary: dict, key: str, value: any, conversion_fn=None):
        """
        Adds a key-value pair to a dictionary if the value is non-empty.
        If a conversion function is supplied, the value will first be converted using that function.
        The key-value pair will only be added if the value is non-empty
        """
        if _is_not_empty(value):
            dictionary[key] = value if conversion_fn is None else conversion_fn(value)

    @staticmethod
    def dictionary(dictionary: dict, key: str, values: dict):
        """
        Adds a key-value pair to a dictionary, where the value is itself a dictionary.
        Any key-value pairs in the values dictionary where the value is empty will first be removed.
        The key-value pair will only be added if at least one of the values is non-empty.
        """
        if any(_is_not_empty(value) for value in values.values()):
            Add.item(dictionary, key, Create.dictionary(values))

    @staticmethod
    def list_of_dict(dictionary: dictionary, key: str, values: dictionary):
        """
        Adds a key-value pair to a dictionary, where the value is a single-item list containing a dictionary.
        Any key-value pairs in the values dictionary where the value is empty will first be removed.
        The key-value pair will only be added if at least one of the values is non-empty.
        """
        if any(_is_not_empty(value) for value in values.values()):
            Add.item(dictionary, key, [Create.dictionary(values)])

    @staticmethod
    def custom_item(dictionary: dictionary, key: str, values: list, value_to_add: any):
        """
        Adds a key-value pair to a dictionary, where the value can take any format.
        The key-value pair will only be added if at least one of the values is non-empty.
        """
        if any(_is_not_empty(value) for value in values):
            dictionary[key] = value_to_add

    @staticmethod
    def snomed(dictionary: dictionary, key: str, code: str, display: str):
        """
        Adds a key-value pair to a dictionary, where the value is snomed code dictionary.
        The key-value pair will only be added if at least one of the code or display is non-empty.
        """
        if any(_is_not_empty(value) for value in [code, display]):
            dictionary[key] = {
                "coding": [Create.dictionary({"system": "http://snomed.info/sct", "code": code, "display": display})]
            }


class Convert:
    """
    Some values need to be converted when the batch input is transformed into FHIR Immunization Resources. Each of the
    conversion functions returns the converted value where possible, or returns the originial value otherwise
    """

    # TODO: Fix data and date_time conversion
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
    def gender_code(code: any) -> any:
        """Converts gender code to fhir gender if the code is recognised. Otherwise returns the original code."""
        code_to_fhir = {"1": "male", "2": "female", "9": "other", "0": "unknown"}
        return code_to_fhir.get(code, code)

    @staticmethod
    def boolean(value: any) -> any:
        """
        Converts value to a Python boolean if the value is a string representation of a boolean.
        Otherwise returns the original value.
        """
        lower_value = value.lower() if isinstance(value, str) else None
        return {"true": True, "false": False}.get(lower_value, value)

    # TODO: Consider whether this should return an integer for integer strings
    @staticmethod
    def decimal(value: any) -> any:
        """
        Converts value to a Decimal if the value is a string representation of a decimal number.
        Otherwise returns the original value.
        """
        try:
            return Decimal(value)
        except (TypeError, ValueError, InvalidOperation):
            return value

    @staticmethod
    def integer(value: any) -> any:
        """
        Converts value to a integer if the value is a string representation of an integer.
        Otherwise returns the original value.
        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return value

    @staticmethod
    def to_lower(value: any) -> any:
        """Converts value to a lower case string if the value is a string. Otherwise returns the original value."""
        try:
            return value.lower()
        except (AttributeError, SyntaxError):
            return value
