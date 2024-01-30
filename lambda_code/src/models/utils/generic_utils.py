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

    questionnaire_reponse = [
        x
        for x in json_data["contained"]
        if x.get("resourceType") == "QuestionnaireResponse"
    ][0]

    item = [x for x in questionnaire_reponse["item"] if x.get("linkId") == link_id][0]

    if answer_type == "valueCoding":
        value = item["answer"][0][answer_type][field_type]

    if answer_type == "valueReference":
        value = item["answer"][0][answer_type]["identifier"][field_type]

    if answer_type in ("valueBoolean", "valueString", "valueDateTime"):
        value = item["answer"][0][answer_type]

    return value


def get_generic_extension_value(
    json_data: dict,
    url: str,
    system: str,
    field_type: Literal["code", "display"],
) -> Union[str, None]:
    """
    Get the value of an extension field, given its url, field_type, and system
    """
    value_codeable_concept_coding = [
        x for x in json_data["extension"] if x.get("url") == url
    ][0]["valueCodeableConcept"]["coding"]

    value = [x for x in value_codeable_concept_coding if x.get("system") == system][0][
        field_type
    ]

    return value


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
    url: str, system: str, field_type: Literal["code", "display"]
) -> str:
    """Generate the field location string for extension items"""
    return (
        f"extension[?(@.url=='{url}')].valueCodeableConcept."
        + f"coding[?(@.system=='{system}')].{field_type}"
    )


def get_deep_attr(obj, attrs):
    for attr in attrs.split("."):
        obj = getattr(obj, attr)
    return obj
