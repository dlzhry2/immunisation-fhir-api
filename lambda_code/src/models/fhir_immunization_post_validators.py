from models.utils.generic_utils import (
    generate_field_location_for_extension,
    generate_field_location_for_questionnnaire_response,
)

from models.utils.post_validation_utils import PostValidation, MandatoryError
from mappings import Mandation, vaccine_type_applicable_validations


class FHIRImmunizationPostValidators:
    """FHIR Immunization Post Validators"""

    @classmethod
    def set_reduce_validation_code(cls, values: dict) -> dict:
        """
        Set reduce_validation_code property to match the value in the JSON data.
        If the field does not exist then assume False.
        """

        reduce_validation_code = "False"

        # If reduce_validation_code field exists then retrieve it's value
        try:
            for record in values["contained"]:
                if record.resource_type == "QuestionnaireResponse":
                    for item in record.item:
                        if item.linkId == "ReduceValidation":
                            if item.answer[0].valueCoding.code:
                                reduce_validation_code = item.answer[0].valueCoding.code
        except KeyError:
            pass

        cls.reduce_validation_code = reduce_validation_code

        return values

    @classmethod
    def validate_vaccination_procedure_code(cls, values: dict) -> dict:
        "Validate that vaccination_procedure_code is a valid code"
        url = (
            "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "VaccinationProcedure"
        )
        field_location = generate_field_location_for_extension(url, "code")
        try:
            vaccination_procedure_code = None
            for record in values["extension"]:
                if record.url == url:
                    vaccination_procedure_code = record.valueCodeableConcept.coding[
                        0
                    ].code
                    break
            if vaccination_procedure_code is None:
                raise KeyError
            cls.vaccine_type = PostValidation.vaccination_procedure_code(
                vaccination_procedure_code, field_location
            )

        except KeyError as error:
            raise MandatoryError(f"{field_location} is a mandatory field") from error

        return values

    @classmethod
    def set_status(cls, values: dict) -> dict:
        "Set status property to match the value in the JSON data"
        # Note: no need to check field is present, as this is done already by the FHIR validator
        cls.status = values["status"]

        return values

    @classmethod
    def validate_patient_identifier_value(cls, values: dict) -> dict:
        "Validate that patient_identifier_value is present or absent, as required"
        field_location = "patient.identifier.value"
        mandation = vaccine_type_applicable_validations["patient_identifier_value"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "patient", "identifier.value", mandation, field_location
        )

        return values

    @classmethod
    def validate_occurrence_date_time(cls, values: dict) -> dict:
        "Validate that occurrence_date_time is present or absent, as required"
        field_location = "occurenceDateTime"
        mandation = vaccine_type_applicable_validations["occurrence_date_time"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "occurrenceDateTime", None, mandation, field_location
        )

        return values

    @classmethod
    def validate_site_code_code(cls, values: dict) -> dict:
        "Validate that site_code_code is present or absent, as required"
        field_location = generate_field_location_for_questionnnaire_response(
            "SiteCode", "code"
        )
        mandation = vaccine_type_applicable_validations["site_code_code"][
            cls.vaccine_type
        ]

        PostValidation.check_questionnaire_link_id_exists(
            values, "SiteCode", "code", mandation, field_location
        )

        return values

    @classmethod
    def validate_site_name_code(cls, values: dict) -> dict:
        "Validate that site_name_code is present or absent, as required"
        field_location = generate_field_location_for_questionnnaire_response(
            "SiteName", "code"
        )
        mandation = vaccine_type_applicable_validations["site_name_code"][
            cls.vaccine_type
        ]

        PostValidation.check_questionnaire_link_id_exists(
            values, "SiteName", "code", mandation, field_location
        )

        return values

    @classmethod
    def validate_identifier_value(cls, values: dict) -> dict:
        "Validate that identifier_value is present or absent, as required"
        field_location = "identifier[0].value"
        mandation = vaccine_type_applicable_validations["identifier_value"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "identifier", "value", mandation, field_location, index=0
        )

        return values

    @classmethod
    def validate_identifier_system(cls, values: dict) -> dict:
        "Validate that identifier_system is present or absent, as required"
        field_location = "identifier[0].system"
        mandation = vaccine_type_applicable_validations["identifier_system"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "identifier", "system", mandation, field_location, index=0
        )

        return values

    @classmethod
    def validate_recorded(cls, values: dict) -> dict:
        "Validate that recorded is present or absent, as required"
        field_location = "recorded"
        mandation = vaccine_type_applicable_validations["recorded"][cls.vaccine_type]

        PostValidation.check_attribute_exists(
            values, "recorded", None, mandation, field_location
        )

        return values

    @classmethod
    def validate_primary_source(cls, values: dict) -> dict:
        "Validate that primarySource is present or absent, as required"
        field_location = "primarySource"
        mandation = vaccine_type_applicable_validations["primary_source"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "primarySource", None, mandation, field_location
        )

        return values

    @classmethod
    def validate_report_origin_text(cls, values: dict) -> dict:
        "Validate that reportOrigin.text is present or absent, as required"
        field_location = "reportOrigin.text"
        mandation = vaccine_type_applicable_validations["report_origin_text"][
            cls.vaccine_type
        ]

        if not values["primarySource"]:
            mandation = Mandation.mandatory

        try:
            PostValidation.check_attribute_exists(
                values, "reportOrigin", "text", mandation, field_location
            )
        except MandatoryError as error:
            raise MandatoryError(
                f"{field_location} is mandatory when primarySource is false"
            ) from error

        return values
