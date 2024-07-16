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


def create_reference_to_patient_resource(patient: dict) -> dict:
    """Creates a reference to the patient which includes the nhs number identifier"""
    patient_nhs_number_identifier = [x for x in patient["identifier"] if x.get("system") == Urls.nhs_number][0]

    return {
        "reference": "MOCK REFERENCE",  # TODO: Where to get reference from?
        "type": "Patient",
        "identifier": patient_nhs_number_identifier,
    }


class Filter:
    """Functions for filtering a FHIR Immunization Resource"""

    @staticmethod
    def read(imms: dict):
        """Apply filtering for READ request"""
        imms.pop("identifier")
        return imms

    @staticmethod
    def search(imms: dict, bundle_patient: dict = None):
        """Apply filtering for an individual FHIR Immunization Resource as part of SEARCH request"""
        imms = remove_reference_to_contained_practitioner(imms)
        imms.pop("contained")
        imms["patient"] = create_reference_to_patient_resource(bundle_patient)
        return imms
