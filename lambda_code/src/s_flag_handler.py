import copy


def handle_s_flag(imms, patient):
    try:
        patient_is_restricted = patient['meta']['security'][0]['display'] == "restricted"
    except (KeyError, IndexError):
        return imms

    if not patient_is_restricted:
        return imms

    result = copy.deepcopy(imms)

    items_to_remove = ["SiteCode", "SiteName"]

    try:
        for record in result["contained"]:
            if record["resourceType"] == "QuestionnaireResponse":
                record["item"] = [item for item in record["item"]
                                  if "linkId" not in item or item["linkId"] not in items_to_remove]
                if not record["item"]:
                    del record["item"]
    except KeyError:
        pass

    return result
