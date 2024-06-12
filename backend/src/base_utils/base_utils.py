"""Utils for backend src code"""

from copy import deepcopy


def remove_questionnaire_items(imms: dict, items_to_remove: list):
    """Removes questionnaire items from an FHIR Immunization Resource"""

    result = deepcopy(imms)

    questionnaire = next(
        (record for record in result.get("contained", []) if record.get("resourceType") == "QuestionnaireResponse"),
        None,
    )

    if questionnaire and questionnaire.get("item"):
        questionnaire["item"] = [
            item for item in questionnaire.get("item", []) if item.get("linkId") not in items_to_remove
        ]

    return result
