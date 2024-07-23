"""Functions for filtering a FHIR Immunization Resource"""

from models.utils.generic_utils import is_actor_referencing_contained_resource, get_contained_practitioner
from constants import Urls


def remove_reference_to_contained_practitioner(imms: dict) -> dict:
    """Remove the reference to a contained patient resource from the performer field (if such a reference exists)"""
    # Obtain contained_practitioner (if it exists)
    try:
        contained_practitioner = get_contained_practitioner(imms)
    except (KeyError, IndexError, AttributeError):
        return imms

    # Remove reference to the contained practitioner from imms[performer]
    contained_practitioner_id = contained_practitioner["id"]
    imms["performer"] = [
        x for x in imms["performer"] if not is_actor_referencing_contained_resource(x, contained_practitioner_id)
    ]

    return imms


def create_reference_to_patient_resource(patient_full_url: str, patient: dict) -> dict:
    """
    Returns a reference to the given patient which includes the patient nhs number identifier (system and value fields
    only) and patient uuid. "Type" field is set to "Patient".
    """
    patient_nhs_number_identifier = [x for x in patient["identifier"] if x.get("system") == Urls.nhs_number][0]

    return {
        "reference": patient_full_url,
        "type": "Patient",
        "identifier": {
            "system": patient_nhs_number_identifier["system"],
            "value": patient_nhs_number_identifier["value"],
        },
    }


def add_use_to_identifier(imms: dict) -> dict:
    """
    Add use of "offical" to immunisation identifier if no use currently specified
    (if use is currently specified it is left as it is i.e. it doesn't get overwritten)
    """
    if "use" not in imms["identifier"][0]:
        imms["identifier"][0]["use"] = "official"
    return imms


class Filter:
    """Functions for filtering a FHIR Immunization Resource"""

    @staticmethod
    def read(imms: dict):
        """Apply filtering for READ request"""
        imms.pop("identifier")
        return imms

    @staticmethod
    def search(imms: dict, patient_full_url: str, bundle_patient: dict = None):
        """Apply filtering for an individual FHIR Immunization Resource as part of SEARCH request"""
        imms = remove_reference_to_contained_practitioner(imms)
        imms.pop("contained")
        imms["patient"] = create_reference_to_patient_resource(patient_full_url, bundle_patient)
        imms = add_use_to_identifier(imms)
        # Location identifier system and value are to be overwritten
        # (for backwards compatibility with Immunisation History API, as agreed with VDS team)
        imms["location"]["identifier"]["system"] = "urn:iso:std:iso:3166"
        imms["location"]["identifier"]["value"] = "GB"
        imms["location"]["type"] = "Location"
        return imms
