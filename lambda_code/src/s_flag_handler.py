def remove_personal_info(data):
    if isinstance(data, dict):
        keys_to_remove = ["SiteCode", "SiteName"]
        
        # Check if "item" is present and remove items with "linkId" in keys_to_remove
        if "item" in data:
            data["item"] = [item for item in data["item"] if "linkId" not in item or item["linkId"] not in keys_to_remove]
            if not data["item"]:
                del data["item"]

        result = {}
        for key, value in data.items():
            # Recursively call remove_personal_info for nested structures
            updated_value = remove_personal_info(value)
            
            # Update value if not in keys_to_remove
            if updated_value is not None:
                result[key] = updated_value

        return result if result else None
    elif isinstance(data, list):
        # Call remove_personal_info for each element in the array and build a new list
        result = [remove_personal_info(object) for object in data if remove_personal_info(object) is not None]
        return result if result else None
    else:
        return data
