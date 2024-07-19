from filter import Filter


def handle_s_flag(imms, patient):
    """
    See https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?pageId=758110223 for details.
    """
    try:
        patient_is_restricted = str.lower(patient["meta"]["security"][0]["code"]) == "r"
    except (KeyError, IndexError):
        return imms

    return Filter.s_flag(imms) if patient_is_restricted else imms
