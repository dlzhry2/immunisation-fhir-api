from models.utils.generic_utils import (
    generate_field_location_for_extension,
    generate_field_location_for_questionnnaire_response,
)

from models.utils.post_validation_utils import PostValidation
from mappings import vaccine_type_applicable_validations


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
            raise ValueError(f"{field_location} is a mandatory field") from error

        return values

    @classmethod
    def set_status(cls, values: dict) -> dict:
        "Set status property to match the value in the JSON data"
        # Note: no need to check field is present, as this is done already by the FHIR validator
        cls.status = values["status"]

        return values

    @classmethod
    def validate_patient_identifier_value(cls, values: dict) -> dict:
        "Validate that vaccination_procedure_code is a valid code"
        field_location = "patient.identifier.value"
        mandation = vaccine_type_applicable_validations["patient_identifier_value"][
            cls.vaccine_type
        ]

        PostValidation.check_attribute_exists(
            values, "patient", "identifier.value", mandation, field_location
        )

        return values
