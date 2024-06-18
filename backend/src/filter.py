"""Functions for filtering a FHIR Immunization Resource"""

from base_utils.base_utils import remove_questionnaire_items


class Filter:
    """Functions for filtering a FHIR Immunization Resource"""

    @staticmethod
    def read(imms: dict):
        """Apply filtering for READ request"""
        imms.pop("identifier")
        imms = remove_questionnaire_items(imms, ["IpAddress", "UserId", "UserName", "UserEmail"])
        return imms
