"""Immunization FHIR R4B validator"""
from fhir.resources.R4B.immunization import Immunization
from models.utils import (
    pre_validate_string,
    pre_validate_date_time,
    pre_validate_list,
    pre_validate_date,
    pre_validate_boolean,
    pre_validate_positive_integer,
    pre_validate_decimal,
    get_generic_questionnaire_response_value,
    get_generic_extension_value,
    generate_field_location_for_questionnnaire_response,
    generate_field_location_for_extension,
)
from models.constants import Constants


class ImmunizationValidator:
    """
    Validate the FHIR Immunization model against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def pre_validate_patient_identifier_value(cls, values: dict) -> dict:
        """
        Pre-validate that, if patient.identifier.value (legacy CSV field name: NHS_NUMBER)
        exists, then it is a string of 10 characters which does not contain spaces
        """
        try:
            patient_identifier_value = values["patient"]["identifier"]["value"]
            pre_validate_string(
                patient_identifier_value,
                "patient.identifier.value",
                defined_length=10,
                spaces_allowed=False,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_occurrence_date_time(cls, values: dict) -> dict:
        """
        Pre-validate that, if occurrenceDateTime exists (legacy CSV field name: DATE_AND_TIME),
        then it is a string in the format "YYYY-MM-DDThh:mm:ss+zz:zz" or "YYYY-MM-DDThh:mm:ss-zz:zz"
        (i.e. date and time, including timezone offset in hours and minutes), representing a valid
        datetime.

        NOTE: occurrenceDateTime is a mandatory FHIR field. A value of None will be rejected by the
        FHIR model before pre-validators are run.
        """
        try:
            occurrence_date_time = values["occurrenceDateTime"]
            pre_validate_date_time(occurrence_date_time, "occurrenceDateTime")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_contained(cls, values: dict) -> dict:
        """Pre-validate that, if contained exists, then it is a list of length 1"""
        try:
            contained = values["contained"]
            pre_validate_list(contained, "contained", defined_length=1)
        except KeyError:
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
            for index, value in enumerate(values["contained"][0]["item"]):
                try:
                    questionnaire_answer = value["answer"]
                    pre_validate_list(
                        questionnaire_answer,
                        "contained[?(@.resourceType=='QuestionnaireResponse')]"
                        + f".item[{index}].answer",
                        defined_length=1,
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_questionnaire_site_code_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SiteCode')].answer[0].valueCoding.code (legacy CSV field name: SITE_CODE)
        exists, then it is a non-empty string
        """
        try:
            questionnaire_site_code_code = get_generic_questionnaire_response_value(
                values, "SiteCode", "code"
            )
            pre_validate_string(
                questionnaire_site_code_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="SiteCode", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_site_name_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SiteName')].answer[0].valueCoding.code (legacy CSV field name: SITE_NAME)
        exists, then it is a non-empty string
        """
        try:
            site_name_code = get_generic_questionnaire_response_value(
                values, "SiteName", "code"
            )
            pre_validate_string(
                site_name_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="SiteName", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_identifier(cls, values: dict) -> dict:
        """
        Pre-validate that, if identifier exists, then it is a list of length 1
        """
        try:
            identifier = values["identifier"]
            pre_validate_list(identifier, "identifier", defined_length=1)
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
            pre_validate_string(identifier_value, "identifier[0].value")
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
            pre_validate_string(identifier_system, "identifier[0].system")
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
            pre_validate_string(status, "status", predefined_values=Constants.STATUSES)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_recorded(cls, values: dict) -> dict:
        """
        Pre-validate that, if recorded (legacy CSV field name: RECORDED_DATE) exists, then it is a
        string in the format YYYY-MM-DD, representing a valid date
        """
        try:
            recorded = values["recorded"]
            pre_validate_date(recorded, "recorded")
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
            pre_validate_boolean(primary_source, "primarySource")
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

            pre_validate_string(report_origin_text, "reportOrigin.text", max_length=100)
        except KeyError:
            pass

        return values

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
                    pre_validate_list(
                        coding,
                        f"extension[{index}].valueCodeableConcept.coding",
                        defined_length=1,
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                vaccination_procedure_code,
                generate_field_location_for_extension(url=url, field_type="code"),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_vaccination_procedure_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationProcedure')].valueCodeableConcept.coding[0].display
        (legacy CSV field name: VACCINATION_PROCEDURE_CODE) exists, then it is a non-empty string
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
            pre_validate_string(
                vaccination_procedure_display,
                generate_field_location_for_extension(url=url, field_type="display"),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                vaccination_situation_code,
                generate_field_location_for_extension(url=url, field_type="code"),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_vaccination_situation_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if extension[?(@.url=='https://fhir.hl7.org.uk/StructureDefinition/
        Extension-UKCore-VaccinationSituation')].valueCodeableConcept.coding[0].display
        (legacy CSV field name: VACCINATION_SITUATION_CODE) exists, then it is a non-empty string
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
            pre_validate_string(
                vaccination_situation_display,
                generate_field_location_for_extension(url=url, field_type="display"),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_status_reason_coding(cls, values: dict) -> dict:
        """
        Pre-validate that, if statusReason.coding (legacy CSV field name: REASON_GIVEN_CODE)
        exists, then it is a list of length 1
        """
        try:
            coding = values["statusReason"]["coding"]
            pre_validate_list(
                coding,
                "statusReason.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_status_reason_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if statusReason.coding[0].code (legacy CSV field location:
        REASON_NOT_GIVEN_CODE) exists, then it is a non-empty string
        """
        try:
            status_reason_coding_code = values["statusReason"]["coding"][0]["code"]
            pre_validate_string(
                status_reason_coding_code, "statusReason.coding[0].code"
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
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
            pre_validate_list(
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
            pre_validate_positive_integer(
                protocol_applied_dose_number_positive_int,
                "protocolApplied[0].doseNumberPositiveInt",
                max_value=9,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_vaccine_code_coding(cls, values: dict) -> dict:
        """Pre-validate that, if vaccineCode.coding exists, then it is a list of length 1"""
        try:
            vaccine_code_coding = values["vaccineCode"]["coding"]
            pre_validate_list(
                vaccine_code_coding,
                "vaccineCode.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_vaccine_code_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if vaccineCode.coding[0].code (legacy CSV field name:
        VACCINE_PRODUCT_CODE) exists, then it is a non-empty string
        """
        try:
            vaccine_code_coding_code = values["vaccineCode"]["coding"][0]["code"]
            pre_validate_string(vaccine_code_coding_code, "vaccineCode.coding[0].code")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_vaccine_code_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if vaccineCode.coding[0].display (legacy CSV field name:
        VACCINE_PRODUCT_TERM) exists, then it is a non-empty string
        """
        try:
            vaccine_code_coding_display = values["vaccineCode"]["coding"][0]["display"]
            pre_validate_string(
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
            pre_validate_string(manufacturer_display, "manufacturer.display")
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
            pre_validate_string(lot_number, "lotNumber", max_length=100)
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
            pre_validate_date(expiration_date, "expirationDate")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_site_coding(cls, values: dict) -> dict:
        """Pre-validate that, if site.coding exists, then it is a list of length 1"""
        try:
            site_coding = values["site"]["coding"]
            pre_validate_list(
                site_coding,
                "site.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_site_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if site.coding[0].code (legacy CSV field name: SITE_OF_VACCINATION_CODE)
        exists, then it is a non-empty string
        """
        try:
            site_coding_code = values["site"]["coding"][0]["code"]
            pre_validate_string(site_coding_code, "site.coding[0].code")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_site_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if site.coding[0].display (legacy CSV field name:
        SITE_OF_VACCINATION_TERM) exists, then it is a non-empty string
        """
        try:
            site_coding_display = values["site"]["coding"][0]["display"]
            pre_validate_string(site_coding_display, "site.coding[0].display")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_route_coding(cls, values: dict) -> dict:
        """Pre-validate that, if route.coding exists, then it is a list of length 1"""
        try:
            route_coding = values["route"]["coding"]
            pre_validate_list(
                route_coding,
                "route.coding",
                defined_length=1,
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_route_coding_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if route.coding[0].code (legacy CSV field name:
        ROUTE_OF_VACCINATION_CODE) exists, then it is a non-empty string
        """
        try:
            route_coding_code = values["route"]["coding"][0]["code"]
            pre_validate_string(route_coding_code, "route.coding[0].code")
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_route_coding_display(cls, values: dict) -> dict:
        """
        Pre-validate that, if route.coding[0].display (legacy CSV field name:
        ROUTE_OF_VACCINATION_TERM) exists, then it is a non-empty string
        """
        try:
            route_coding_display = values["route"]["coding"][0]["display"]
            pre_validate_string(route_coding_display, "route.coding[0].display")
        except KeyError:
            pass

        return values

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
            pre_validate_decimal(
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
            pre_validate_string(dose_quantity_code, "doseQuantity.code")
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
            pre_validate_string(dose_quantity_unit, "doseQuantity.unit")
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
                    pre_validate_list(
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
                    pre_validate_string(
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
        (legacy CSV field name: INDICATION_CODE) is a non-empty string
        """
        try:
            for index, value in enumerate(values["reasonCode"]):
                try:
                    reason_code_coding_display = value["coding"][0]["display"]
                    pre_validate_string(
                        reason_code_coding_display,
                        f"reasonCode[{index}].coding[0].display",
                    )
                except KeyError:
                    pass
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_nhs_number_status_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='NhsNumberStatus')].answer[0].valueCoding.code (legacy CSV field name:
        NHS_NUMBER_STATUS_INDICATOR_CODE) exists, then it is a non-empty string
        """
        try:
            nhs_number_status_code = get_generic_questionnaire_response_value(
                values, "NhsNumberStatus", "code"
            )
            pre_validate_string(
                nhs_number_status_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="NhsNumberStatus", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                nhs_number_status_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="NhsNumberStatus", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
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
            pre_validate_string(
                local_patient_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="LocalPatient", field_type="code"
                ),
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
            pre_validate_string(
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
            pre_validate_string(
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
            pre_validate_string(
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
            pre_validate_string(
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
            pre_validate_string(
                care_setting_display,
                generate_field_location_for_questionnnaire_response(
                    link_id="CareSetting", field_type="display"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                ip_address_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="IpAddress", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                user_id_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserId", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                user_name_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserName", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

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
            pre_validate_string(
                user_email_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="UserEmail", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_submitted_time_stamp_code(cls, values: dict) -> dict:
        """
        Pre-validate that, if contained[?(@.resourceType=='QuestionnaireResponse')]
        .item[?(@.linkId=='SubmittedTimeStamp')].answer[0].valueCoding.code (legacy CSV field name:
        SUBMITTED_TIMESTAMP) exists, then it is a non-empty string
        """
        try:
            user_email_code = get_generic_questionnaire_response_value(
                values, "SubmittedTimeStamp", "code"
            )
            pre_validate_date_time(
                user_email_code,
                generate_field_location_for_questionnnaire_response(
                    link_id="SubmittedTimeStamp", field_type="code"
                ),
            )
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """
        Add custom NHS validators to the model

        NOTE: THE ORDER IN WHICH THE VALIDATORS ARE ADDED IS IMPORTANT! DO NOT CHANGE THE ORDER
        WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST.
        """
        # DO NOT CHANGE THE ORDER WITHOUT UNDERSTANDING THE IMPACT ON OTHER VALIDATORS IN THE LIST
        Immunization.add_root_validator(
            self.pre_validate_patient_identifier_value, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_occurrence_date_time, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_contained, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_questionnaire_answers, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_questionnaire_site_code_code, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_site_name_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier_value, pre=True)
        Immunization.add_root_validator(self.pre_validate_identifier_system, pre=True)
        Immunization.add_root_validator(self.pre_validate_status, pre=True)
        Immunization.add_root_validator(self.pre_validate_recorded, pre=True)
        Immunization.add_root_validator(self.pre_validate_primary_source, pre=True)
        Immunization.add_root_validator(self.pre_validate_report_origin_text, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_extension_value_codeable_concept_codings, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_vaccination_procedure_code, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_vaccination_procedure_display, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_vaccination_situation_code, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_vaccination_situation_display, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_status_reason_coding, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_status_reason_coding_code, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_status_reason_coding_display, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_protocol_applied, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_protocol_applied_dose_number_positive_int, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_vaccine_code_coding, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_vaccine_code_coding_code, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_vaccine_code_coding_display, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_manufacturer_display, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_lot_number, pre=True)
        Immunization.add_root_validator(self.pre_validate_expiration_date, pre=True)
        Immunization.add_root_validator(self.pre_validate_site_coding, pre=True)
        Immunization.add_root_validator(self.pre_validate_site_coding_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_site_coding_display, pre=True)
        Immunization.add_root_validator(self.pre_validate_route_coding, pre=True)
        Immunization.add_root_validator(self.pre_validate_route_coding_code, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_route_coding_display, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_dose_quantity_value, pre=True)
        Immunization.add_root_validator(self.pre_validate_dose_quantity_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_dose_quantity_unit, pre=True)
        Immunization.add_root_validator(self.pre_validate_reason_code_codings, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_reason_code_coding_codes, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_reason_code_coding_displays, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_nhs_number_status_code, pre=True
        )
        Immunization.add_root_validator(
            self.pre_validate_nhs_number_status_display, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_site_code_system, pre=True)
        Immunization.add_root_validator(self.pre_validate_local_patient_code, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_local_patient_system, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_consent_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_consent_display, pre=True)
        Immunization.add_root_validator(self.pre_validate_care_setting_code, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_care_setting_display, pre=True
        )
        Immunization.add_root_validator(self.pre_validate_ip_address_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_user_id_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_user_name_code, pre=True)
        Immunization.add_root_validator(self.pre_validate_user_email_code, pre=True)
        Immunization.add_root_validator(
            self.pre_validate_submitted_time_stamp_code, pre=True
        )

    def validate(self, json_data) -> Immunization:
        """Generate the Immunization model"""
        immunization = Immunization.parse_obj(json_data)
        return immunization
