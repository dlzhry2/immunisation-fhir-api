from models.utils.generic_utils import (
    get_generic_questionnaire_response_value,
    get_generic_extension_value,
    generate_field_location_for_questionnnaire_response,
    generate_field_location_for_extension,
)
from models.utils.pre_validator_utils import PreValidation
from models.constants import Constants


class FHIRImmunizationPreValidators:
    """Some stuff"""

    # TODO: all patient and practitioner validations need to be moved into here as they are now
    # contained resources
    # -----------------------------------------------------------------------------------------

    @classmethod
    def pre_validate_contained(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained exists, then  each resourceType is unique
        """
        try:
            contained = values["contained"]
            PreValidation.for_unique_list(
                contained,
                "resourceType",
                "contained[?(@.resourceType=='FIELD_TO_REPLACE')]",
            )

        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_patient_identifier(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='Patient')].identifier exists, then it
        is a list of length 1
        """
        try:
            patient_identifier = [
                x for x in values["contained"] if x.get("resourceType") == "Patient"
            ][0]["identifier"]
            PreValidation.for_list(
                patient_identifier,
                "contained[?(@.resourceType=='Patient')].identifier",
                defined_length=1,
            )
        except (KeyError, IndexError):
            pass

        return values

    @classmethod
    def pre_validate_patient_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if patient.identifier.value (legacy CSV field name: NHS_NUMBER)
        exists, then it is a string of 10 characters which does not contain spaces
        """
        try:
            patient_identifier_value = [
                x for x in values["contained"] if x.get("resourceType") == "Patient"
            ][0]["identifier"][0]["value"]

            PreValidation.for_string(
                patient_identifier_value,
                "contained[?(@.resourceType=='Patient')].identifier[0].value",
                defined_length=10,
                spaces_allowed=False,
            )
        except (KeyError, IndexError):
            pass

        return values

    @classmethod
    def pre_validate_occurrence_date_time(cls, values: dict) -> dict:
        """
        Pre-validate that, if occurrenceDateTime exists (legacy CSV field name: DATE_AND_TIME),
        then it is a string in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or "YYYY-MM-DDThh:mm:ss-zz:zz"
        (i.e. date and time, including timezone offset in hours and minutes), representing a valid
        datetime. Milliseconds are optional after the seconds (e.g. 2021-01-01T00:00:00.000+00:00)."

        NOTE: occurrenceDateTime is a mandatory FHIR field. A value of None will be rejected by the
        FHIR model before pre-validators are run.
        """
        try:
            occurrence_date_time = values["occurrenceDateTime"]
            PreValidation.for_date_time(occurrence_date_time, "occurrenceDateTime")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_questionnaire_response_item(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')].item exists,
        then each linkId is unique
        """
        try:
            questionnaire_response_item = [
                x
                for x in values["contained"]
                if x.get("resourceType") == "QuestionnaireResponse"
            ][0]["item"]

            PreValidation.for_unique_list(
                questionnaire_response_item,
                "linkId",
                "contained[?(@.resourceType=='QuestionnaireResponse')]"
                + ".item[?(@.linkId=='FIELD_TO_REPLACE')]",
            )

        except (KeyError, IndexError):
            pass

        return values

    @classmethod
    def pre_validate_questionnaire_answers(cls, values: dict) -> dict:
        """
        Pre-validate that, if they exist, each
        contained[?(@.resourceType=='QuestionnaireResponse')].item[index].answer
        is a list of length 1
        """
        try:
            questionnaire_items = [
                x
                for x in values["contained"]
                if x.get("resourceType") == "QuestionnaireResponse"
            ][0]["item"]
            for index, value in enumerate(questionnaire_items):
                try:
                    questionnaire_answer = value["answer"]
                    PreValidation.for_list(
                        questionnaire_answer,
                        "contained[?(@.resourceType=='QuestionnaireResponse')]"
                        + f".item[{index}].answer",
                        defined_length=1,
                    )
                except KeyError:
                    pass
        except (KeyError, IndexError):
            pass

        return values

    # TODO: Handle scenario where item.get("actor") = None (? can except attribute error)
    @classmethod
    def pre_validate_performer_actor_type(cls, values: dict) -> dict:
        """
        Pre-validate that, if performer.actor.organisation exists, then there is only one such
        key with the value of "Organization"
        """
        try:
            found = []
            for item in values["performer"]:
                if (
                    item.get("actor").get("type") == "Organization"
                    and item.get("actor").get("type") in found
                ):
                    raise ValueError(
                        "performer.actor[?@.type=='Organization'] must be unique"
                    )

                found.append(item.get("actor").get("type"))

        except KeyError:
            pass

        return values

    # TODO: Handle scenario where item.get("actor") = None (? can except attribute error)
    @classmethod
    def pre_validate_performer_actor_reference(cls, values: dict) -> dict:
        """
        Pre-validate that, if performer.actor.organisation exists, then there is only one such
        key with the value of "Organization"
        """
        try:
            # Obtain the contained_practitioner_id
            contained_practitioner = [
                x
                for x in values["contained"]
                if x.get("resourceType") == "Practitioner"
            ][0]
            contained_practitioner_id = "#" + contained_practitioner["id"]

            # Check that there is exactly one performer_actor_reference which matches the
            # contained_practitioner_id
            performer_actor_references = []
            for item in values.get("performer", []):
                # If more than one reference contains the id then raise an error
                if (
                    item.get("actor").get("reference") == contained_practitioner_id
                    and item.get("actor").get("reference") in performer_actor_references
                ):
                    raise ValueError(
                        f"{contained_practitioner_id} must be referenced by exactly ONE "
                        + "performer.actor"
                    )

                performer_actor_references.append(item.get("actor").get("reference"))

            # If no reference contains the id then raise an erro
            if contained_practitioner_id not in performer_actor_references:
                raise ValueError(
                    f"{contained_practitioner_id} must be referenced by exactly ONE "
                    + "performer.actor"
                )

        except (KeyError, IndexError):
            pass

        return values

    # TODO: Handle scenario where item.get("actor") = None (? can except attribute error)
    # TODO: ?Add tests for the above scenario
    @classmethod
    def pre_validate_organization_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if performer[?(@.actor.type=='Organization').identifier.value]
        (legacy CSV field name: SITE_CODE) exists, then it is a non-empty string
        """
        try:
            organization_identifier_value = [
                x
                for x in values["performer"]
                if x.get("actor").get("type") == "Organization"
            ][0]["actor"]["identifier"]["value"]
            PreValidation.for_string(
                organization_identifier_value,
                "performer[?(@.actor.type=='Organization')].actor.identifier.value",
            )
        except (KeyError, IndexError):
            pass

        return values

    # TODO: Handle scenario where item.get("actor") = None (? can except attribute error)
    @classmethod
    def pre_validate_organization_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SiteName')].answer[0].valueCoding.code (legacy CSV field name: SITE_NAME)
        exists, then it is a non-empty string
        """
        try:
            organization_display = [
                x
                for x in values["performer"]
                if x.get("actor").get("type") == "Organization"
            ][0]["actor"]["display"]
            PreValidation.for_string(
                organization_display,
                "performer[?@.actor.type == 'Organization'].actor.display",
            )
        except (KeyError, IndexError):
            pass

        return values

    @classmethod
    def pre_validate_identifier(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier exists, then it is a list of length 1
        """
        try:
            identifier = values["identifier"]
            PreValidation.for_list(identifier, "identifier", defined_length=1)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].value (legacy CSV field name: UNIQUE_ID) exists,
        then it is a non-empty string
        """
        try:
            identifier_value = values["identifier"][0]["value"]
            PreValidation.for_string(identifier_value, "identifier[0].value")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier[0].system (legacy CSV field name: UNIQUE_ID_URI) exists,
        then it is a non-empty string
        """
        try:
            identifier_system = values["identifier"][0]["system"]
            PreValidation.for_string(identifier_system, "identifier[0].system")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_status(cls, values: dict) -> dict:
        """
        Pre-validate that, if status (legacy CSV field names ACTION_FLAG or NOT_GIVEN) exists,
        then it is a non-empty string which is one of the following: completed, entered-in-error,
        not-done.

        NOTE 1: ACTION_FLAG and NOT_GIVEN are mutually exclusive i.e. if ACTION_FLAG is present then
        NOT_GIVEN will be absent and vice versa. The ACTION_FLAGs are 'completed' and 'not-done'.
        The following 1-to-1 mapping applies:
        * NOT_GIVEN is True <---> Status will be set to 'not-done' (and therefore ACTION_FLAG is
            absent)
        * NOT_GIVEN is False <---> Status will be set to 'completed' or 'entered-in-error' (and
            therefore ACTION_FLAG is present)

        NOTE 2: Status is a mandatory FHIR field. A value of None will be rejected by the
        FHIR model before pre-validators are run.
        """
        try:
            status = values["status"]
            PreValidation.for_string(
                status, "status", predefined_values=Constants.STATUSES
            )
        except KeyError:
            pass

        return values

    # TODO: Check with martin that this is still just a date and not date time
    @classmethod
    def pre_validate_recorded(cls, values: dict) -> dict:
        """
        Pre-validate that, if recorded (legacy CSV field name: RECORDED_DATE) exists, then it is a
        string in the format YYYY-MM-DD, representing a valid date
        """
        try:
            recorded = values["recorded"]
            PreValidation.for_date(recorded, "recorded")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_primary_source(cls, values: dict) -> dict:
        """
        Pre-validate that, if primarySource (legacy CSV field name: PRIMARY_SOURCE) exists,
        then it is a boolean
        """
        try:
            primary_source = values["primarySource"]
            PreValidation.for_boolean(primary_source, "primarySource")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_report_origin_text(cls, values: dict) -> dict:
        """
        Pre-validate that, if reportOrigin.text (legacy CSV field name: REPORT_ORIGIN_TEXT)
        exists, then it is a non-empty string with maximum length 100 characters
        """
        try:
            report_origin_text = values["reportOrigin"]["text"]

            PreValidation.for_string(
                report_origin_text, "reportOrigin.text", max_length=100
            )
        except KeyError:
            pass

        return values

    # TODO: need to check that the coding[*] system is unique for each extension
    # TODO: remove this when the above in complete
    @classmethod
    def pre_validate_extension_value_codeable_concept_codings(
        cls, values: dict
    ) -> dict:
        """
        Pre-validate that, if they exist, each extension[{index}].valueCodeableConcept.coding
        is a list of length 1
        """
        try:
            for index, value in enumerate(values["extension"]):
                try:
                    coding = value["valueCodeableConcept"]["coding"]
                    PreValidation.for_list(
                        coding,
                        f"extension[{index}].valueCodeableConcept.coding",
                        defined_length=1,
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
    # Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system==
    # 'http://snomed.info/sct')].code
    @classmethod
    def pre_validate_vaccination_procedure_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[0].code
        (legacy CSV field name: VACCINATION_PROCEDURE_CODE) exists, then it is a non-empty string
        """
        try:
            url = (
                "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
                + "VaccinationProcedure"
            )
            vaccination_procedure_code = get_generic_extension_value(
                values,
                url,
                "code",
            )
            PreValidation.for_string(
                vaccination_procedure_code,
                generate_field_location_for_extension(url=url, field_type="code"),
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
    # Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[?(@.system==
    # 'http://snomed.info/sct')].display
    @classmethod
    def pre_validate_vaccination_procedure_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[0].display
        (legacy CSV field name: VACCINATION_PROCEDURE_TERM) exists, then it is a non-empty string
        """
        try:
            url = (
                "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
                + "VaccinationProcedure"
            )
            vaccination_procedure_display = get_generic_extension_value(
                values,
                url,
                "display",
            )
            PreValidation.for_string(
                vaccination_procedure_display,
                generate_field_location_for_extension(url=url, field_type="display"),
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
    # Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[?(@.system==
    # 'http://snomed.info/sct')].code
    # TODO: amend the test to run on the not-done data
    @classmethod
    def pre_validate_vaccination_situation_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[0].code
        (legacy CSV field name: VACCINATION_SITUATION_CODE) exists, then it is a non-empty string
        """
        try:
            url = (
                "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
                + "VaccinationSituation"
            )
            vaccination_situation_code = get_generic_extension_value(
                values,
                url,
                "code",
            )
            PreValidation.for_string(
                vaccination_situation_code,
                generate_field_location_for_extension(url=url, field_type="code"),
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
    # Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[?(@.system==
    # 'http://snomed.info/sct')].display
    # TODO: amend the test to run on the not-done data
    @classmethod
    def pre_validate_vaccination_situation_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[0].display
        (legacy CSV field name: VACCINATION_SITUATION_TERM) exists, then it is a non-empty string
        """
        try:
            url = (
                "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-"
                + "VaccinationSituation"
            )
            vaccination_situation_display = get_generic_extension_value(
                values,
                url,
                "display",
            )
            PreValidation.for_string(
                vaccination_situation_display,
                generate_field_location_for_extension(url=url, field_type="display"),
            )
        except KeyError:
            pass

        return values

    # TODO: amend the test to run on the not-done data
    @classmethod
    def pre_validate_status_reason_coding(cls, values: dict) -> dict:
        """
        Pre-validate that, if statusReason.coding (legacy CSV field name: REASON_GIVEN_CODE)
        exists, then it is a list of length 1
        """
        try:
            coding = values["statusReason"]["coding"]
            PreValidation.for_list(
                coding,
                "statusReason.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    # TODO: amend the test to run on the not-done data
    @classmethod
    def pre_validate_status_reason_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if statusReason.coding[0].code (legacy CSV field location:
        REASON_NOT_GIVEN_CODE) exists, then it is a non-empty string
        """
        try:
            status_reason_coding_code = values["statusReason"]["coding"][0]["code"]
            PreValidation.for_string(
                status_reason_coding_code, "statusReason.coding[0].code"
            )
        except KeyError:
            pass

        return values

    # TODO: amend the test to run on the not-done data
    @classmethod
    def pre_validate_status_reason_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if statusReason.coding[0].display (legacy CSV field name:
        REASON_NOT_GIVEN_TERM) exists, then it is a non-empty string
        """
        try:
            status_reason_coding_display = values["statusReason"]["coding"][0][
                "display"
            ]
            PreValidation.for_string(
                status_reason_coding_display, "statusReason.coding[0].display"
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_protocol_applied(cls, values: dict) -> dict:
        """Pre-validate that, if protocolApplied exists, then it is a list of length 1"""
        try:
            protocol_applied = values["protocolApplied"]
            PreValidation.for_list(
                protocol_applied,
                "protocolApplied",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_protocol_applied_dose_number_positive_int(
        cls, values: dict
    ) -> dict:
        """
        Pre-validate that, if protocolApplied[0].doseNumberPositiveInt (legacy CSV fidose_sequence)
        exists, then it is an integer from 1 to 9
        """
        try:
            protocol_applied_dose_number_positive_int = values["protocolApplied"][0][
                "doseNumberPositiveInt"
            ]
            PreValidation.for_positive_integer(
                protocol_applied_dose_number_positive_int,
                "protocolApplied[0].doseNumberPositiveInt",
                max_value=9,
            )
        except KeyError:
            pass

        return values

    # TODO: need to check that the coding[*] system is unique
    # TODO: remove this when the above in complete
    @classmethod
    def pre_validate_vaccine_code_coding(cls, values: dict) -> dict:
        """Pre-validate that, if vaccineCode.coding exists, then it is a list of length 1"""
        try:
            vaccine_code_coding = values["vaccineCode"]["coding"]
            PreValidation.for_list(
                vaccine_code_coding,
                "vaccineCode.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # vaccineCode.coding[?(@.system=='http://snomed.info/sct')].code
    @classmethod
    def pre_validate_vaccine_code_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if vaccineCode.coding[0].code (legacy CSV field name:
        VACCINE_PRODUCT_CODE) exists, then it is a non-empty string
        """
        try:
            vaccine_code_coding_code = values["vaccineCode"]["coding"][0]["code"]
            PreValidation.for_string(
                vaccine_code_coding_code, "vaccineCode.coding[0].code"
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # vaccineCode.coding[?(@.system=='http://snomed.info/sct')].display
    @classmethod
    def pre_validate_vaccine_code_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if vaccineCode.coding[0].display (legacy CSV field name:
        VACCINE_PRODUCT_TERM) exists, then it is a non-empty string
        """
        try:
            vaccine_code_coding_display = values["vaccineCode"]["coding"][0]["display"]
            PreValidation.for_string(
                vaccine_code_coding_display, "vaccineCode.coding[0].display"
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_manufacturer_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if manufacturer.display (legacy CSV field name: VACCINE_MANUFACTURER)
        exists, then it is a non-empty string
        """
        try:
            manufacturer_display = values["manufacturer"]["display"]
            PreValidation.for_string(manufacturer_display, "manufacturer.display")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_lot_number(cls, values: dict) -> dict:
        """
        Pre-validate that, if lotNumber (legacy CSV field name: BATCH_NUMBER) exists,
        then it is a non-empty string
        """
        try:
            lot_number = values["lotNumber"]
            PreValidation.for_string(lot_number, "lotNumber", max_length=100)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_expiration_date(cls, values: dict) -> dict:
        """
        Pre-validate that, if expirationDate (legacy CSV field name: EXPIRY_DATE) exists,
        then it is a string in the format YYYY-MM-DD, representing a valid date
        """
        try:
            expiration_date = values["expirationDate"]
            PreValidation.for_date(expiration_date, "expirationDate")
        except KeyError:
            pass

        return values

    # TODO: need to check that the coding[*] system is unique
    # TODO: remove this when the above in complete
    @classmethod
    def pre_validate_site_coding(cls, values: dict) -> dict:
        """Pre-validate that, if site.coding exists, then it is a list of length 1"""
        try:
            site_coding = values["site"]["coding"]
            PreValidation.for_list(
                site_coding,
                "site.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # site.coding[?(@.system=='http://snomed.info/sct')].code
    @classmethod
    def pre_validate_site_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if site.coding[0].code (legacy CSV field name: SITE_OF_VACCINATION_CODE)
        exists, then it is a non-empty string
        """
        try:
            site_coding_code = values["site"]["coding"][0]["code"]
            PreValidation.for_string(site_coding_code, "site.coding[0].code")
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # site.coding[?(@.system=='http://snomed.info/sct')].display
    @classmethod
    def pre_validate_site_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if site.coding[0].display (legacy CSV field name:
        SITE_OF_VACCINATION_TERM) exists, then it is a non-empty string
        """
        try:
            site_coding_display = values["site"]["coding"][0]["display"]
            PreValidation.for_string(site_coding_display, "site.coding[0].display")
        except KeyError:
            pass

        return values

    # TODO: need to check that the coding[*] system is unique
    # TODO: remove this when the above in complete
    @classmethod
    def pre_validate_route_coding(cls, values: dict) -> dict:
        """Pre-validate that, if route.coding exists, then it is a list of length 1"""
        try:
            route_coding = values["route"]["coding"]
            PreValidation.for_list(
                route_coding,
                "route.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # route.coding[?(@.system=='http://snomed.info/sct')].code
    @classmethod
    def pre_validate_route_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if route.coding[0].code (legacy CSV field name:
        ROUTE_OF_VACCINATION_CODE) exists, then it is a non-empty string
        """
        try:
            route_coding_code = values["route"]["coding"][0]["code"]
            PreValidation.for_string(route_coding_code, "route.coding[0].code")
        except KeyError:
            pass

        return values

    # TODO: change coding[0] to look for "http://snomed.info/sct"
    # route.coding[?(@.system=='http://snomed.info/sct')].display
    @classmethod
    def pre_validate_route_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if route.coding[0].display (legacy CSV field name:
        ROUTE_OF_VACCINATION_TERM) exists, then it is a non-empty string
        """
        try:
            route_coding_display = values["route"]["coding"][0]["display"]
            PreValidation.for_string(route_coding_display, "route.coding[0].display")
        except KeyError:
            pass

        return values

    # TODO: need to validate that doseQuantity.system is "http://unitsofmeasure.org"
    @classmethod
    def pre_validate_dose_quantity_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if doseQuantity.value (legacy CSV field name: DOSE_AMOUNT) exists,
        then it is a number representing an integer or decimal with
        maximum four decimal places

        NOTE: This validator will only work if the raw json data is parsed with the
        parse_float argument set to equal Decimal type (Decimal must be imported from decimal).
        Floats (but not integers) will then be parsed as Decimals.
        e.g json.loads(raw_data, parse_float=Decimal)
        """
        try:
            dose_quantity_value = values["doseQuantity"]["value"]
            PreValidation.for_integer_or_decimal(
                dose_quantity_value, "doseQuantity.value", max_decimal_places=4
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_dose_quantity_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if doseQuantity.code (legacy CSV field name: DOSE_UNIT_CODE) exists,
        then it is a non-empty string
        """
        try:
            dose_quantity_code = values["doseQuantity"]["code"]
            PreValidation.for_string(dose_quantity_code, "doseQuantity.code")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_dose_quantity_unit(cls, values: dict) -> dict:
        """
        Pre-validate that, if doseQuantity.unit (legacy CSV field name: DOSE_UNIT_TERM) exists,
        then it is a non-empty string
        """
        try:
            dose_quantity_unit = values["doseQuantity"]["unit"]
            PreValidation.for_string(dose_quantity_unit, "doseQuantity.unit")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_reason_code_codings(cls, values: dict) -> dict:
        """
        Pre-validate that, if they exist, each reasonCode[{index}].coding is a list of length 1
        """
        try:
            for index, value in enumerate(values["reasonCode"]):
                try:
                    reason_code_coding = value["coding"]
                    PreValidation.for_list(
                        reason_code_coding,
                        f"reasonCode[{index}].coding",
                        defined_length=1,
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_reason_code_coding_codes(cls, values: dict) -> dict:
        """
        Pre-validate that, if they exist, each reasonCode[{index}].coding[0].code
        (legacy CSV field name: INDICATION_CODE) is a non-empty string
        """
        try:
            for index, value in enumerate(values["reasonCode"]):
                try:
                    reason_code_coding_code = value["coding"][0]["code"]
                    PreValidation.for_string(
                        reason_code_coding_code, f"reasonCode[{index}].coding[0].code"
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_reason_code_coding_displays(cls, values: dict) -> dict:
        """
        Pre-validate that, if they exist, each reasonCode[{index}].coding[0].display
        (legacy CSV field name: INDICATION_TERM) is a non-empty string
        """
        try:
            for index, value in enumerate(values["reasonCode"]):
                try:
                    reason_code_coding_display = value["coding"][0]["display"]
                    PreValidation.for_string(
                        reason_code_coding_display,
                        f"reasonCode[{index}].coding[0].display",
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    # TODO: check that the url is unique
    # TODO: need to check that the coding[*] system is unique
    # TODO: change where we get nhs_number_status_code from
    # (to contained[?(@.resourceType=='Patient')].extension[?(@.url==
    # 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus')]
    # .valueCodeableConcept.coding[?(@.system==
    # 'https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland')].code)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_nhs_number_status_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='Patient')].extension[?(@.url==
        'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus')]
        .valueCodeableConcept.coding[0].code (legacy CSV field name: NHS_NUMBER_STATUS_INDICATOR_CODE)
        exists, then it is a non-empty string
        """
        try:
            nhs_number_status_code = get_generic_questionnaire_response_value(
                values, "NhsNumberStatus", "code"
            )
            PreValidation.for_string(
                nhs_number_status_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="NhsNumberStatus", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    # TODO: change where we get nhs_number_status_display from
    # (to contained[?(@.resourceType=='Patient')].extension[?(@.url==
    # 'https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus')]
    # .valueCodeableConcept.coding[?(@.system==
    # 'https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland')].display)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_nhs_number_status_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='NhsNumberStatus')].answer[0].valueCoding.display (legacy CSV field name:
        NHS_NUMBER_STATUS_INDICATOR_DESCRIPTION) exists, then it is a non-empty string
        """
        try:
            nhs_number_status_display = get_generic_questionnaire_response_value(
                values, "NhsNumberStatus", "display"
            )
            PreValidation.for_string(
                nhs_number_status_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="NhsNumberStatus", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values

    # TODO: search for actor type organization
    # change where we get site_code_system from
    # (to performer[?@.actor.type == "Organization"].actor.identifier.system)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_site_code_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SiteCode')].answer[0].valueCoding.system (legacy CSV field name:
        SITE_CODE_TYPE_URI) exists, then it is a non-empty string
        """
        try:
            site_code_system = get_generic_questionnaire_response_value(
                values, "SiteCode", "system"
            )
            PreValidation.for_string(
                site_code_system,
                generate_field_location_for_questionnnaire_response(
                    link_id="SiteCode", field_type="system"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_local_patient_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='LocalPatient')].answer[0].valueCoding.code (legacy CSV field name:
        LOCAL_PATIENT_ID) exists, then it is a non-empty string
        """
        try:
            local_patient_code = get_generic_questionnaire_response_value(
                values, "LocalPatient", "code"
            )
            PreValidation.for_string(
                local_patient_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="LocalPatient", field_type="code"
                ),
                max_length=20,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_local_patient_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='LocalPatient')].answer[0].valueCoding.system (legacy CSV field name:
        LOCAL_PATIENT_URI) exists, then it is a non-empty string
        """
        try:
            local_patient_system = get_generic_questionnaire_response_value(
                values, "LocalPatient", "system"
            )
            PreValidation.for_string(
                local_patient_system,
                generate_field_location_for_questionnnaire_response(
                    link_id="LocalPatient", field_type="system"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_consent_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='Consent')].answer[0].valueCoding.code (legacy CSV field name:
        CONSENT_FOR_TREATMENT_CODE) exists, then it is a non-empty string
        """
        try:
            consent_code = get_generic_questionnaire_response_value(
                values, "Consent", "code"
            )
            PreValidation.for_string(
                consent_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="Consent", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_consent_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='Consent')].answer[0].valueCoding.display (legacy CSV field name:
        CONSENT_FOR_TREATMENT_DESCRIPTION) exists, then it is a non-empty string
        """
        try:
            consent_display = get_generic_questionnaire_response_value(
                values, "Consent", "display"
            )
            PreValidation.for_string(
                consent_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="Consent", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_care_setting_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='CareSetting')].answer[0].valueCoding.code (legacy CSV field name:
        CARE_SETTING_TYPE_CODE) exists, then it is a non-empty string
        """
        try:
            care_setting_code = get_generic_questionnaire_response_value(
                values, "CareSetting", "code"
            )
            PreValidation.for_string(
                care_setting_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="CareSetting", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_care_setting_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='CareSetting')].answer[0].valueCoding.display (legacy CSV field name:
        CARE_SETTING_TYPE_DESCRIPTION) exists, then it is a non-empty string
        """
        try:
            care_setting_display = get_generic_questionnaire_response_value(
                values, "CareSetting", "display"
            )
            PreValidation.for_string(
                care_setting_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="CareSetting", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values

    # change where we get ip_address_code from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='IpAddress')].answer[0].valueString)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_ip_address_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='IpAddress')].answer[0].valueCoding.code (legacy CSV field name:
        IP_ADDRESS) exists, then it is a non-empty string
        """
        try:
            ip_address_code = get_generic_questionnaire_response_value(
                values, "IpAddress", "code"
            )
            PreValidation.for_string(
                ip_address_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="IpAddress", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    # change where we get user_id_code from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='UserId')].answer[0].valueString)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_user_id_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='UserId')].answer[0].valueCoding.code (legacy CSV field name:
        USER_ID) exists, then it is a non-empty string
        """
        try:
            user_id_code = get_generic_questionnaire_response_value(
                values, "UserId", "code"
            )
            PreValidation.for_string(
                user_id_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserId", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    # change where we get user_name from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='UserName')].answer[0].valueString)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_user_name_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='UserName')].answer[0].valueCoding.code (legacy CSV field name:
        USER_NAME) exists, then it is a non-empty string
        """
        try:
            user_name_code = get_generic_questionnaire_response_value(
                values, "UserName", "code"
            )
            PreValidation.for_string(
                user_name_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserName", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    # change where we get user_email_code from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='UserEmail')].answer[0].valueString)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_user_email_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='UserEmail')].answer[0].valueCoding.code (legacy CSV field name:
        USER_EMAIL) exists, then it is a non-empty string
        """
        try:
            user_email_code = get_generic_questionnaire_response_value(
                values, "UserEmail", "code"
            )
            PreValidation.for_string(
                user_email_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserEmail", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    # change where we get submitted_time_stamp_code from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='SubmittedTimeStamp')].answer[0].valueDateTime)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_submitted_time_stamp_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SubmittedTimeStamp')].answer[0].valueCoding.code (legacy CSV field name:
        SUBMITTED_TIMESTAMP), then it is a string in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or
        "YYYY-MM-DDThh:mm:ss-zz:zz" (i.e. date and time, including timezone offset in hours and
        minutes), representing a valid datetime.
        """
        try:
            submitted_time_stamp_code = get_generic_questionnaire_response_value(
                values, "SubmittedTimeStamp", "code"
            )
            PreValidation.for_date_time(
                submitted_time_stamp_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="SubmittedTimeStamp", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_location_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if location.identifier.value (legacy CSV field name: LOCATION_CODE)
        exists, then it is a non-empty string
        """
        try:
            location_identifier_value = values["location"]["identifier"]["value"]
            PreValidation.for_string(
                location_identifier_value, "location.identifier.value"
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_location_identifier_system(cls, values: dict) -> dict:
        """
        Pre-validate that, if location.identifier.system (legacy CSV field name:
        LOCATION_CODE_TYPE_URI) exists, then it is a non-empty string
        """
        try:
            location_identifier_system = values["location"]["identifier"]["system"]
            PreValidation.for_string(
                location_identifier_system, "location.identifier.system"
            )
        except KeyError:
            pass

        return values

    # change where we get reduce_validation_code from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='ReduceValidation')].answer[0].valueBoolean)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_reduce_validation_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='ReduceValidation')].answer[0].valueCoding.code (legacy CSV field name:
        REDUCE_VALIDATION_CODE) exists, then it is a non-empty string
        """
        try:
            reduce_validation_code = get_generic_questionnaire_response_value(
                values, "ReduceValidation", "code"
            )
            PreValidation.for_string(
                reduce_validation_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="ReduceValidation", field_type="code"
                ),
                predefined_values=Constants.REDUCE_VALIDATION_CODES,
            )
        except KeyError:
            pass

        return values

    # change where we get reduce_validation_display from
    # (to contained[?(@.resourceType=='QuestionnaireResponse')]
    # .item[?(@.linkId=='ReduceValidationReason')].answer[0].valueString)
    # TODO: change name of method to match new location
    @classmethod
    def pre_validate_reduce_validation_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='ReduceValidation')].answer[0].valueCoding.display (legacy CSV field name:
        REDUCE_VALIDATION_REASON) exists, then it is a non-empty string
        """
        try:
            reduce_validation_display = get_generic_questionnaire_response_value(
                values, "ReduceValidation", "display"
            )
            PreValidation.for_string(
                reduce_validation_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="ReduceValidation", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values
