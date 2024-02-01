import copy


def handle_s_flag(imms, patient):
    """
    See https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?pageId=758110223 for details.
    """
    try:
        patient_is_restricted = str.lower(patient['meta']['security'][0]['code']) == "r"
    except (KeyError, IndexError):
        return imms

    if not patient_is_restricted:
        return imms

    result = copy.deepcopy(imms)

    questionnaire = next((record for record in result["contained"] if record["resourceType"] == "QuestionnaireResponse"), None)

    # Handle Questionnaire SiteCode
    site_code = next((item for item in questionnaire["item"] if item["linkId"] == "SiteCode"), None)
    if site_code:
        if site_code["answer"] is list and len(site_code["answer"] > 0):
            site_code["answer"] = [site_code["answer"][0]]
        try:
            site_code["answer"][0]["valueCoding"]["code"] = "N2N9I"
        except KeyError:
            pass

    # Handle Questionnaire removals
    questionnaire_items_to_remove = ["SiteName", "Consent"]
    questionnaire["item"] = [item for item in questionnaire["item"]
                             if "linkId" not in item or item["linkId"] not in questionnaire_items_to_remove]

    # Handle reportOrigin
    try:
        del result["reportOrigin"]
    except KeyError:
        pass

    # Handle performer's identifier's system
    for performer in result["performer"]:
        try:
            performer["actor"]["identifier"]["system"] = "https://fhir.nhs.uk/Id/ods-organization-code"
            performer["actor"]["identifier"]["value"] = "N2N9I"
        except KeyError:
            pass

    # Handle Location
    try:
        del result["location"]
    except KeyError:
        pass

    return result
