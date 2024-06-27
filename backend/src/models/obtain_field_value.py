"""Functions for obtaining a field value from the FHIR immunization resource json data"""

from models.utils.generic_utils import (
    get_contained_patient,
    get_contained_practitioner,
    is_organization,
    get_generic_extension_value,
)
from constants import Urls


class ObtainFieldValue:
    """Functions for obtaining a field value from the FHIR immunization resource json data"""

    def __init__(self) -> None:
        pass

    @staticmethod
    def occurrence_date_time(imms: dict):
        """Obtains occurrence_date_time value"""
        return imms["occurrenceDateTime"]

    @staticmethod
    def patient_identifier_value(imms: dict):
        """Obtains patient_identifier_value value"""
        contained_patient = get_contained_patient(imms)
        contained_patient_identifier = [
            x for x in contained_patient.get("identifier") if x.get("system") == Urls.nhs_number
        ][0]
        return contained_patient_identifier["value"]

    @staticmethod
    def patient_name_given(imms: dict):
        """Obtains patient_name_given value"""
        return get_contained_patient(imms)["name"][0]["given"]

    @staticmethod
    def patient_name_family(imms: dict):
        """Obtains patient_name_family value"""
        return get_contained_patient(imms)["name"][0]["family"]

    @staticmethod
    def patient_birth_date(imms: dict):
        """Obtains patient_birth_date value"""
        return get_contained_patient(imms)["birthDate"]

    @staticmethod
    def patient_gender(imms: dict):
        """Obtains patient_gender value"""
        return get_contained_patient(imms)["gender"]

    @staticmethod
    def patient_address_postal_code(imms: dict):
        """Obtains patient_address_postal_code value"""
        return get_contained_patient(imms)["address"][0]["postalCode"]

    @staticmethod
    def organization_identifier_value(imms: dict):
        return [x for x in imms.get("performer") if is_organization(x)][0]["actor"]["identifier"]["value"]

    @staticmethod
    def organization_display(imms: dict):
        return [x for x in imms.get("performer") if is_organization(x)][0]["actor"]["display"]

    @staticmethod
    def identifier_value(imms: dict):
        return imms["identifier"][0]["value"]

    @staticmethod
    def identifier_system(imms: dict):
        return imms["identifier"][0]["system"]

    @staticmethod
    def practitioner_name_given(imms: dict):
        return get_contained_practitioner(imms)["name"][0]["given"]

    @staticmethod
    def practitioner_name_family(imms: dict):
        return get_contained_practitioner(imms)["name"][0]["family"]

    @staticmethod
    def practitioner_identifier_value(imms: dict):
        return get_contained_practitioner(imms)["identifier"][0]["value"]

    @staticmethod
    def practitioner_identifier_system(imms: dict):
        return get_contained_practitioner(imms)["identifier"][0]["system"]

    @staticmethod
    def recorded(imms: dict):
        return imms["recorded"]

    @staticmethod
    def primary_source(imms: dict):
        return imms["primarySource"]

    @staticmethod
    def report_origin_text(imms: dict):
        return imms["reportOrigin"]["text"]

    @staticmethod
    def vaccination_procedure_code(imms: dict):
        return get_generic_extension_value(imms, Urls.vaccination_procedure, Urls.snomed, "code")

    @staticmethod
    def vaccination_procedure_display(imms: dict):
        return get_generic_extension_value(imms, Urls.vaccination_procedure, Urls.snomed, "display")

    @staticmethod
    def dose_number_positive_int(imms: dict):
        return imms["protocolApplied"][0]["doseNumberPositiveInt"]

    @staticmethod
    def vaccine_code_coding_code(imms: dict):
        return [x for x in imms["vaccineCode"]["coding"] if x.get("system") == Urls.snomed][0]["code"]

    @staticmethod
    def vaccine_code_coding_display(imms: dict):
        return [x for x in imms["vaccineCode"]["coding"] if x.get("system") == Urls.snomed][0]["display"]

    @staticmethod
    def manufacturer_display(imms: dict):
        return imms["manufacturer"]["display"]

    @staticmethod
    def lot_number(imms: dict):
        return imms["lotNumber"]

    @staticmethod
    def expiration_date(imms: dict):
        return imms["expirationDate"]

    @staticmethod
    def site_coding_code(imms: dict):
        return [x for x in imms["site"]["coding"] if x.get("system") == Urls.snomed][0]["code"]

    @staticmethod
    def site_coding_display(imms: dict):
        return [x for x in imms["site"]["coding"] if x.get("system") == Urls.snomed][0]["display"]

    @staticmethod
    def route_coding_code(imms: dict):
        return [x for x in imms["route"]["coding"] if x.get("system") == Urls.snomed][0]["code"]

    @staticmethod
    def route_coding_display(imms: dict):
        return [x for x in imms["route"]["coding"] if x.get("system") == Urls.snomed][0]["display"]

    @staticmethod
    def dose_quantity_value(imms: dict):
        return imms["doseQuantity"]["value"]

    @staticmethod
    def dose_quantity_code(imms: dict):
        return imms["doseQuantity"]["code"]

    @staticmethod
    def dose_quantity_unit(imms: dict):
        return imms["doseQuantity"]["unit"]

    @staticmethod
    def nhs_number_verification_status_code(imms: dict):
        patient_identifier = get_contained_patient(imms)["identifier"]
        patient_identifier_extension_item = [x for x in patient_identifier if x.get("system") == Urls.nhs_number][0]
        nhs_number_verification_status_code = get_generic_extension_value(
            patient_identifier_extension_item,
            url=Urls.nhs_number_verification_status_structure_definition,
            system=Urls.nhs_number_verification_status_code_system,
            field_type="code",
        )
        return nhs_number_verification_status_code

    @staticmethod
    def nhs_number_verification_status_display(imms: dict):
        patient_identifier = get_contained_patient(imms)["identifier"]
        patient_identifier_extension_item = [x for x in patient_identifier if x.get("system") == Urls.nhs_number][0]
        nhs_number_verification_status_display = get_generic_extension_value(
            patient_identifier_extension_item,
            url=Urls.nhs_number_verification_status_structure_definition,
            system=Urls.nhs_number_verification_status_code_system,
            field_type="display",
        )
        return nhs_number_verification_status_display

    @staticmethod
    def organization_identifier_system(imms: dict):
        return [x for x in imms.get("performer") if is_organization(x)][0]["actor"]["identifier"]["system"]

    @staticmethod
    def location_identifier_value(imms: dict):
        return imms["location"]["identifier"]["value"]

    @staticmethod
    def location_identifier_system(imms: dict):
        return imms["location"]["identifier"]["system"]

    @staticmethod
    def reason_code_coding_code(imms: dict, index: int):
        return imms["reasonCode"][index]["coding"][0]["code"]

    @staticmethod
    def reason_code_coding_display(imms: dict, index: int):
        return imms["reasonCode"][index]["coding"][0]["display"]
