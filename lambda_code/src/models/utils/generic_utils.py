"""Generic utilities for models"""

from typing import Literal, Union


def get_generic_questionnaire_response_value(
    json_data: dict, link_id: str, field_type: Literal["code", "display", "system"]
) -> Union[str, None]:
    """
    Get the value of a QuestionnaireResponse field, given its linkId
    """

    for record in json_data["contained"]:
        if record["resourceType"] == "QuestionnaireResponse":
            for item in record["item"]:
                if item["linkId"] == link_id:
                    return item["answer"][0]["valueCoding"][field_type]

    raise KeyError(
        "$.contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0].valueCoding.{field_type}"
    )


def get_generic_extension_value(
    json_data: dict, url: str, field_type: Literal["code", "display", "system"]
) -> Union[str, None]:
    """
    Get the value of an extension field, given its url
    """
    for record in json_data["extension"]:
        if record["url"] == url:
            return record["valueCodeableConcept"]["coding"][0][field_type]

    raise KeyError(
        f"$.extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type} does not exist"
    )


def generate_field_location_for_questionnnaire_response(
    link_id: str, field_type: Literal["code", "display", "system"]
) -> str:
    """Generate the field location string for questionnaire response items"""
    return (
        "contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0].valueCoding.{field_type}"
    )


def generate_field_location_for_extension(
    url: str, field_type: Literal["code", "display"]
) -> str:
    """Generate the field location string for extension items"""
    return f"extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type}"
