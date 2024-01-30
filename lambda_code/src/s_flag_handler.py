def handle_s_flag(imms, patient):
    patient_is_restricted = patient['meta']['security'][0]['display'] == "restricted"
    if not patient_is_restricted:
        return imms

    def recurse(imms):
        if isinstance(imms, dict):
            keys_to_remove = ["SiteCode", "SiteName"]

            # Check if "item" is present and remove items with "linkId" in keys_to_remove
            if "item" in imms:
                imms["item"] = [item for item in imms["item"] if "linkId" not in item or item["linkId"] not in keys_to_remove]
                if not imms["item"]:
                    del imms["item"]

            result = {}
            for key, value in imms.items():
                # Recursively call remove_personal_info for nested structures
                updated_value = recurse(value)

                # Update value if not in keys_to_remove
                if updated_value is not None:
                    result[key] = updated_value

            return result if result else None
        elif isinstance(imms, list):
            # Call remove_personal_info for each element in the array and build a new list
            result = [recurse(object) for object in imms if recurse(object) is not None]
            return result if result else None
        else:
            return imms

    recurse(imms)
