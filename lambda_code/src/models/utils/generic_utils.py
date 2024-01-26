"""Generic utilities for models"""

from typing import Literal, Union, Optional, Any


def get_generic_questionnaire_response_value(
    json_data: dict,
    link_id: str,
    answer_type: Literal["valueBoolean", "valueString", "valueDateTime", "valueCoding"],
    field_type: Optional[Literal["code", "display", "system"]] = None,
) -> Any:
    """
    Get the value of a QuestionnaireResponse field, given its linkId

    Parameters:-
    json_data: dict
        The json data to be validated
    answer_type: Literal["valueBoolean", "valueString", "valueDateTime", "valueCoding"]
        The answer type to be validated
    link_id: str
        The linkId of the field to be validated
    value_coding_field_type: Optional[Literal["code", "display", "system"]]
        The value coding field type to be validated, must be provided for valueCoding fields
    """

    error_msg = (
        "$.contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0]"
    )

    questionnaire_reponse = [
        x
        for x in json_data["contained"]
        if x.get("resourceType") == "QuestionnaireResponse"
    ][0]

    item = [x for x in questionnaire_reponse["item"] if x.get("linkId") == link_id][0]

    if answer_type == "valueCoding":
        error_msg = f"{error_msg}.{answer_type}.{field_type}"
        return item["answer"][0][answer_type][field_type]

    if answer_type == "valueReference":
        error_msg = f"{error_msg}.{answer_type}.identifier.{field_type}"
        return item["answer"][0][answer_type]["identifier"][field_type]

    if answer_type in ("valueBoolean", "valueString", "valueDateTime"):
        error_msg = f"{error_msg}.{answer_type}"
        return item["answer"][0][answer_type]

    raise KeyError(error_msg)


# TODO : Access value using list comprehension
def get_generic_extension_value(
    json_data: dict,
    url: str,
    field_type: Literal["code", "display", "system"],
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
    link_id: str,
    answer_type: str,
    field_type: Literal["code", "display", "system"] = None,
) -> str:
    """Generate the field location string for questionnaire response items"""
    location = (
        "contained[?(@.resourceType=='QuestionnaireResponse')]"
        + f".item[?(@.linkId=='{link_id}')].answer[0]"
    )
    if answer_type == "valueCoding":
        return f"{location}.{answer_type}.{field_type}"
    if answer_type == "valueReference":
        return f"{location}.{answer_type}.identifier.{field_type}"
    if answer_type in ("valueBoolean", "valueString", "valueDateTime"):
        return f"{location}.{answer_type}"


def generate_field_location_for_extension(
    url: str, field_type: Literal["code", "display"]
) -> str:
    """Generate the field location string for extension items"""
    return f"extension[?(@.url=='{url}')].valueCodeableConcept.coding[0].{field_type}"
