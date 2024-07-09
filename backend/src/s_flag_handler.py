import copy


def handle_s_flag(imms, patient):
    """
    See https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?pageId=758110223 for details.
    """
    try:
        patient_is_restricted = str.lower(patient["meta"]["security"][0]["code"]) == "r"
    except (KeyError, IndexError):
        return imms

    if not patient_is_restricted:
        return imms

    result = copy.deepcopy(imms)

   
    contained_patient = next(
        (
            record
            for record in result.get("contained", [])
            if record["resourceType"] == "Patient"
        ),
        None,
    )

    # Handle Questionnaire SiteCode
    performer_actor_organization = next(
        (
            item
            for item in result["performer"]
            if item.get("actor", {}).get("type") == "Organization"
        ),
        None,
    )

    if performer_actor_organization:
        try:
            performer_actor_organization["actor"]["identifier"]["value"] = "N2N9I"
            performer_actor_organization["actor"]["identifier"][
                "system"
            ] = "https://fhir.nhs.uk/Id/ods-organization-code"
        except KeyError:
            pass
        
    if contained_patient:
        try:
            contained_patient["address"][0]["postalCode"] = "ZZ99 3CZ"
        except (KeyError, IndexError):
            pass
    
    # Handle Location
    try:
        del result["location"]
    except KeyError:
        pass

    return result
