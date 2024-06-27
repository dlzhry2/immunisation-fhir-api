"""Generic utilities"""

import datetime

from typing import Literal, Union, Optional, Any


def get_contained_resource(imms: dict, resource: Literal["Patient", "Practitioner", "QuestionnaireResponse"]):
    """Extract and return the requested contained resource from the FHIR Immunization Resource JSON data"""
    return [x for x in imms.get("contained") if x.get("resourceType") == resource][0]


def get_contained_patient(imms: dict):
    """Extract and return the contained patient from the FHIR Immunization Resource JSON data"""
    return get_contained_resource(imms, "Patient")


def get_contained_practitioner(imms: dict):
    """Extract and return the contained practitioner from the FHIR Immunization Resource JSON data"""
    return get_contained_resource(imms, "Practitioner")


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

    questionnaire_reponse = [x for x in json_data["contained"] if x.get("resourceType") == "QuestionnaireResponse"][0]

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
    value_codeable_concept_coding = [x for x in json_data["extension"] if x.get("url") == url][0][
        "valueCodeableConcept"
    ]["coding"]

    value = [x for x in value_codeable_concept_coding if x.get("system") == system][0][field_type]

    return value


def generate_field_location_for_questionnaire_response(
    link_id: str,
    answer_type: str,
    field_type: Literal["code", "display", "system"] = None,
) -> str:
    """Generate the field location string for questionnaire response items"""
    location = "contained[?(@.resourceType=='QuestionnaireResponse')]" + f".item[?(@.linkId=='{link_id}')].answer[0]"
    if answer_type == "valueCoding":
        return f"{location}.{answer_type}.{field_type}"
    if answer_type == "valueReference":
        return f"{location}.{answer_type}.identifier.{field_type}"
    if answer_type in ("valueBoolean", "valueString", "valueDateTime"):
        return f"{location}.{answer_type}"


def generate_field_location_for_extension(url: str, system: str, field_type: Literal["code", "display"]) -> str:
    """Generate the field location string for extension items"""
    return f"extension[?(@.url=='{url}')].valueCodeableConcept." + f"coding[?(@.system=='{system}')].{field_type}"


def is_organization(x):
    """Returns boolean indicating whether the input dictionary is for an organization"""
    try:
        return x["actor"]["type"] == "Organization"
    except KeyError:
        return False


def nhs_number_mod11_check(nhs_number: str) -> bool:
    """
    Parameters:-
    nhs_number: str
        The NHS number to be checked.
    Returns:-
        True if the nhs number passes the mod 11 check, False otherwise.

    Definition of NHS number can be found at:
    https://www.datadictionary.nhs.uk/attributes/nhs_number.html
    """
    is_mod11 = False
    if nhs_number.isdigit() and len(nhs_number) == 10:
        # Create a reversed list of weighting factors
        weighting_factors = list(range(2, 11))[::-1]
        # Multiply each of the first nine digits by the weighting factor and add the results of each multiplication
        # together
        total = sum(int(digit) * weight for digit, weight in zip(nhs_number[:-1], weighting_factors))
        # Divide the total by 11 and establish the remainder and subtract the remainder from 11 to give the check digit.
        # If the result is 11 then a check digit of 0 is used. If the result is 10 then the NHS NUMBER is invalid and
        # not used.
        check_digit = 0 if (total % 11 == 0) else (11 - (total % 11))
        # Check the remainder matches the check digit. If it does not, the NHS NUMBER is invalid.
        is_mod11 = check_digit == int(nhs_number[-1])

    return is_mod11


def get_target_disease_codes(immunization: dict):
    """Takes a FHIR immunization resource and returns a list of target disease codes"""
    target_diseases = []
    target_disease_list = immunization.get("protocolApplied")[0].get("targetDisease")
    for element in target_disease_list:
        code = [x.get("code") for x in element.get("coding") if x.get("system") == "http://snomed.info/sct"][0]
        if code is not None:
            target_diseases.append(code)
    return target_diseases


def get_occurrence_datetime(immunization: dict) -> Optional[datetime.datetime]:
    occurrence_datetime_str: Optional[str] = immunization.get("occurrenceDateTime", None)
    if occurrence_datetime_str is None:
        return None

    return datetime.datetime.fromisoformat(occurrence_datetime_str)


def create_diagnostics():
    diagnostics = f"Validation errors: contained[?(@.resourceType=='Patient')].identifier[0].value does not exists."
    exp_error = {"diagnostics": diagnostics}
    return exp_error


def create_diagnostics_error(value):
    if value == "Unauthorized":
        diagnostics = f"{value} system"
        exp_error = {"diagnostics": diagnostics, "error": {value}}
        return exp_error
    if value == "Both":
        diagnostics = (
            f"Validation errors: identifier[0].system and identifier[0].value doesn't match with the stored content"
        )
    else:
        diagnostics = f"Validation errors: identifier[0].{value} doesn't match with the stored content"
    exp_error = {"diagnostics": diagnostics}
    return exp_error
