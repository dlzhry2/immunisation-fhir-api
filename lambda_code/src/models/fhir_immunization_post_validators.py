from models.utils.generic_utils import (
    get_generic_questionnaire_response_value_from_model,
    get_generic_extension_value_from_model,
    generate_field_location_for_extension,
    generate_field_location_for_questionnnaire_response,
)

from models.utils.post_validation_utils import (
    PostValidation,
    MandatoryError,
    NotApplicableError,
)
from mappings import Mandation, vaccine_type_applicable_validations

check_mandation_requirements_met = PostValidation.check_mandation_requirements_met
get_generic_field_value = PostValidation.get_generic_field_value
get_generic_questionnaire_response_value = (
    PostValidation.get_generic_questionnaire_response_value
)


class FHIRImmunizationPostValidators:
    """FHIR Immunization Post Validators"""

    @classmethod
    def set_reduce_validation(cls, values: dict) -> dict:
        """
        Set reduce_validation_code property to match the value in the JSON data.
        If the field does not exist then assume False.
        """
        reduce_validation_code = False

        # If reduce_validation_code field exists then retrieve it's value
        try:
            reduce_validation_code = (
                get_generic_questionnaire_response_value_from_model(
                    values, "ReduceValidation", "valueBoolean"
                )
            )
        except (KeyError, IndexError, AttributeError):
            pass
        finally:
            # If no value is given, then ReduceValidation default value is False
            if reduce_validation_code is None:
                reduce_validation_code = False

        cls.reduce_validation_code = reduce_validation_code

        return values

    @classmethod
    def validate_and_set_vaccination_procedure_code(cls, values: dict) -> dict:
        "Validate that vaccination_procedure_code is a valid code"
        url = (
            "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
            + "VaccinationProcedure"
        )
        system = "http://snomed.info/sct"
        field_type = "code"
        field_location = generate_field_location_for_extension(url, system, field_type)

        try:
            vaccination_procedure_code = get_generic_extension_value_from_model(
                values, url, system, field_type
            )
            if vaccination_procedure_code is None:
                raise KeyError
            cls.vaccine_type = PostValidation.vaccination_procedure_code(
                vaccination_procedure_code, field_location
            )

        except (KeyError, IndexError) as error:
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
        try:
            contained_patient_identifier = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0].identifier

            patient_identifier_value = [
                x
                for x in contained_patient_identifier
                if x.system == "https://fhir.nhs.uk/Id/nhs-number"
            ][0].value
        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_identifier_value = None

        check_mandation_requirements_met(
            field_value=patient_identifier_value,
            field_location="contained[?(@.resourceType=='Patient')].identifier[0].value",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_identifier_value",
        )
        return values

    @classmethod
    def validate_patient_name_given(cls, values: dict) -> dict:
        "Validate that patient_name_given is present or absent, as required"
        try:
            contained_patient = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0]

            patient_name_given = contained_patient.name[0].given

        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_name_given = None

        check_mandation_requirements_met(
            field_value=patient_name_given,
            field_location="contained[?(@.resourceType=='Patient')].name[0].given",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_name_given",
        )
        return values

    @classmethod
    def validate_patient_name_family(cls, values: dict) -> dict:
        "Validate that patient_name_family is present or absent, as required"
        try:
            contained_patient = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0]

            patient_name_family = contained_patient.name[0].family

        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_name_family = None

        check_mandation_requirements_met(
            field_value=patient_name_family,
            field_location="contained[?(@.resourceType=='Patient')].name[0].family",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_name_family",
        )
        return values

    @classmethod
    def validate_patient_birth_date(cls, values: dict) -> dict:
        "Validate that patient_birth_date is present or absent, as required"
        try:
            patient_birth_date = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0].birthDate

        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_birth_date = None

        check_mandation_requirements_met(
            field_value=patient_birth_date,
            field_location="contained[?(@.resourceType=='Patient')].birthDate",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_birth_date",
        )
        return values

    @classmethod
    def validate_patient_gender(cls, values: dict) -> dict:
        "Validate that patient_gender is present or absent, as required"
        try:
            patient_gender = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0].gender

        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_gender = None

        check_mandation_requirements_met(
            field_value=patient_gender,
            field_location="contained[?(@.resourceType=='Patient')].gender",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_gender",
        )
        return values

    @classmethod
    def validate_patient_address_postal_code(cls, values: dict) -> dict:
        "Validate that patient_address_postal_code is present or absent, as required"
        try:
            contained_patient = [
                x for x in values["contained"] if x.resource_type == "Patient"
            ][0]

            patient_address_postal_code = contained_patient.address[0].postalCode

        except (KeyError, IndexError, AttributeError, MandatoryError):
            patient_address_postal_code = None

        check_mandation_requirements_met(
            field_value=patient_address_postal_code,
            field_location="contained[?(@.resourceType=='Patient')].address[0].postalCode",
            vaccine_type=cls.vaccine_type,
            mandation_key="patient_address_postal_code",
        )
        return values

    @classmethod
    def validate_occurrence_date_time(cls, values: dict) -> dict:
        "Validate that occurrence_date_time is present or absent, as required"
        field_value = get_generic_field_value(values=values, key="occurrenceDateTime")

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="occurenceDateTime",
            vaccine_type=cls.vaccine_type,
            mandation_key="occurrence_date_time",
        )

        return values

    @classmethod
    def validate_organization_identifier_value(cls, values: dict) -> dict:
        """
        Validate that performer[?(@.actor.type=='Organization')].actor.identifier.value is present
        or absent, as required
        """

        def util_func(x):
            try:
                return x.actor.type == "Organization"
            except AttributeError:
                return False

        try:
            field_value = [x for x in values["performer"] if util_func(x)][
                0
            ].actor.identifier.value
        except (KeyError, IndexError, AttributeError):
            field_value = None

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="performer[?(@.actor.type=='Organization')].actor.identifier.value",
            vaccine_type=cls.vaccine_type,
            mandation_key="organization_identifier_value",
        )

        return values

    @classmethod
    def validate_organization_display(cls, values: dict) -> dict:
        """
        Validate that performer[?@.actor.type == 'Organization'].actor.display is present or
        absent, as required
        """

        def util_func(x):
            try:
                return x.actor.type == "Organization"
            except AttributeError:
                return False

        try:
            field_value = [x for x in values["performer"] if util_func(x)][
                0
            ].actor.display
        except (KeyError, IndexError, AttributeError):
            field_value = None

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="performer[?(@.actor.type=='Organization')].actor.display",
            vaccine_type=cls.vaccine_type,
            mandation_key="organization_display",
        )

        return values

    @classmethod
    def validate_identifier_value(cls, values: dict) -> dict:
        "Validate that identifier_value is present or absent, as required"
        field_value = get_generic_field_value(
            values, "identifier", index=0, attribute="value"
        )

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="identifier[0].value",
            vaccine_type=cls.vaccine_type,
            mandation_key="identifier_value",
        )

        return values

    @classmethod
    def validate_identifier_system(cls, values: dict) -> dict:
        "Validate that identifier_system is present or absent, as required"
        field_value = get_generic_field_value(
            values, "identifier", index=0, attribute="system"
        )

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="identifier[0].system",
            vaccine_type=cls.vaccine_type,
            mandation_key="identifier_system",
        )

        return values

    @classmethod
    def validate_practitioner_name_given(cls, values: dict) -> dict:
        "Validate that practitioner_name_given is present or absent, as required"
        try:
            contained_practitioner = [
                x for x in values["contained"] if x.resource_type == "Practitioner"
            ][0]

            practitioner_name_given = contained_practitioner.name[0].given

        except (KeyError, IndexError, AttributeError, MandatoryError, TypeError):
            practitioner_name_given = None

        check_mandation_requirements_met(
            field_value=practitioner_name_given,
            field_location="contained[?(@.resourceType=='Practitioner')].name[0].given",
            vaccine_type=cls.vaccine_type,
            mandation_key="practitioner_name_given",
        )
        return values

    @classmethod
    def validate_practitioner_name_family(cls, values: dict) -> dict:
        "Validate that practitioner_name_family is present or absent, as required"
        try:
            contained_practitioner = [
                x for x in values["contained"] if x.resource_type == "Practitioner"
            ][0]

            practitioner_name_family = contained_practitioner.name[0].family

        except (KeyError, IndexError, AttributeError, MandatoryError, TypeError):
            practitioner_name_family = None

        check_mandation_requirements_met(
            field_value=practitioner_name_family,
            field_location="contained[?(@.resourceType=='Practitioner')].name[0].family",
            vaccine_type=cls.vaccine_type,
            mandation_key="practitioner_name_family",
        )
        return values

    @classmethod
    def validate_practitioner_identifier_value(cls, values: dict) -> dict:
        "Validate that practitioner_identifier_value is present or absent, as required"
        try:
            contained_practitioner = [
                x for x in values["contained"] if x.resource_type == "Practitioner"
            ][0]

            practitioner_identifier_value = contained_practitioner.identifier[0].value

        except (KeyError, IndexError, AttributeError, MandatoryError):
            practitioner_identifier_value = None

        check_mandation_requirements_met(
            field_value=practitioner_identifier_value,
            field_location="contained[?(@.resourceType=='Practitioner')].identifier[0].value",
            vaccine_type=cls.vaccine_type,
            mandation_key="practitioner_identifier_value",
        )
        return values

    # TODO: Check with imms team r.e. Conditional mandatory logic
    @classmethod
    def validate_practitioner_identifier_system(cls, values: dict) -> dict:
        "Validate that practitioner_identifier_system is present or absent, as required"
        field_location = (
            "contained[?(@.resourceType=='Practitioner')].identifier[0].system"
        )

        try:
            contained_practitioner = [
                x for x in values["contained"] if x.resource_type == "Practitioner"
            ][0]

            practitioner_identifier_system = contained_practitioner.identifier[0].system

        except (KeyError, IndexError, AttributeError, MandatoryError):
            practitioner_identifier_system = None

        # Handle conditional mandation logic
        try:
            contained_practitioner = (
                [x for x in values["contained"] if x.resource_type == "Practitioner"][0]
                .identifier[0]
                .value
            )

            # If practioner_identifier_value is present and vaccine type is COVID-19 or FLU,
            # t then practitioner_identifier_system is mandatory
            if cls.vaccine_type == "COVID-19" or cls.vaccine_type == "FLU":
                mandation = Mandation.mandatory

            if practitioner_identifier_system is None:
                if mandation == Mandation.mandatory:
                    raise MandatoryError(
                        f"{field_location} is mandatory when contained"
                        + "[?(@.resourceType=='Practitioner')].identifier[0].system is present"
                    )

            if mandation == Mandation.not_applicable:
                raise NotApplicableError(
                    f"{field_location} must not be provided for this vaccine type"
                )

        except (KeyError, IndexError, AttributeError):
            check_mandation_requirements_met(
                field_value=practitioner_identifier_system,
                field_location="contained[?(@.resourceType=='Practitioner')].identifier[0].system",
                vaccine_type=cls.vaccine_type,
                mandation_key="practitioner_identifier_system",
            )

        return values

    @classmethod
    def validate_performer_sds_job_role(cls, values: dict) -> dict:
        "Validate that performer_sds_job_role is present or absent, as required"
        field_location = (
            "contained[?(@.resourceType=='QuestionnaireResponse')]"
            + ".item[?(@.linkId=='PerformerSDSJobRole')].answer[0].valueString"
        )

        try:
            performer_sds_job_role = (
                get_generic_questionnaire_response_value_from_model(
                    values, "PerformerSDSJobROle", "valueString"
                )
            )

        except (KeyError, IndexError, AttributeError, MandatoryError):
            performer_sds_job_role = None

        check_mandation_requirements_met(
            field_value=performer_sds_job_role,
            field_location=field_location,
            vaccine_type=cls.vaccine_type,
            mandation_key="performer_sds_job_role",
        )
        return values

    @classmethod
    def validate_recorded(cls, values: dict) -> dict:
        "Validate that recorded is present or absent, as required"
        field_value = get_generic_field_value(
            values,
            "recorded",
        )

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="recorded",
            vaccine_type=cls.vaccine_type,
            mandation_key="recorded",
        )

        return values

    @classmethod
    def validate_primary_source(cls, values: dict) -> dict:
        "Validate that primarySource is present or absent, as required"
        field_value = get_generic_field_value(
            values,
            "primarySource",
        )

        check_mandation_requirements_met(
            field_value=field_value,
            field_location="primarySource",
            vaccine_type=cls.vaccine_type,
            mandation_key="primary_source",
        )

        return values

    @classmethod
    def validate_report_origin_text(cls, values: dict) -> dict:
        "Validate that reportOrigin.text is present or absent, as required"
        field_location = "reportOrigin.text"
        report_origin_text = get_generic_field_value(
            values,
            "reportOrigin",
            attribute="text",
        )
        mandation = vaccine_type_applicable_validations["report_origin_text"][
            cls.vaccine_type
        ]

        if not values["primarySource"]:
            mandation = Mandation.mandatory

        if report_origin_text is None:
            if mandation == Mandation.mandatory:
                raise MandatoryError(
                    f"{field_location} is mandatory when primarySource is false"
                )

        if mandation == Mandation.not_applicable:
            raise NotApplicableError(
                f"{field_location} must not be provided for this vaccine type"
            )

        return values
