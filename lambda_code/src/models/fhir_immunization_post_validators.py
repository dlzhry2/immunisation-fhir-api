from models.utils.generic_utils import (
    generate_field_location_for_extension,
)


from models.utils.post_validation_utils import PostValidation


class FHIRImmunizationPostValidators:
    """FHIR Immunization Post Validators"""

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
            cls.vaccine_type = PostValidation.vaccination_procedure_code(
                vaccination_procedure_code, field_location
            )

        except KeyError as error:
            raise ValueError(f"{field_location} is a mandatory field") from error

        return values
