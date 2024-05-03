""""Decorators to add the relevant fields to the FHIR immunization resource from the batch stream"""

from collections import OrderedDict
import inspect
from typing import List, Callable, Dict, Optional

from batch.errors import DecoratorError, TransformerFieldError, TransformerUnhandledError, TransformerRowError
from batch.utils import _is_not_empty, _add_questionnaire_item_to_list, Create, Add, Convert


ImmunizationDecorator = Callable[[Dict, OrderedDict[str, str]], Optional[DecoratorError]]
"""
A decorator function (Callable) takes current immunization object, validates it and adds appropriate fields to it. 
It returns None if no error occurs, otherwise it returns an error object that has a list of all field errors. 
DO NOT raise any exception during this process. The caller will catch exceptions and treat them as unhandled errors. 
This way we can log these errors which are bugs or a result of a batch file with unexpected headers/values.
NOTE: The decorators are order independent. They can be called in any order, so don't rely on previous changes.
NOTE: decorate function is the only public function. If you add a new decorator, call it in this function.
NOTE: Validation should be handled by the API validator wherever possible. Immunization decorators should only
perform validation that is essential for the transformation to take place.
NOTE: An overarching data rule is that where data is not present the field should not be added to the FHIR Immunization
resource. Therefore before adding an element it is necessary to check that at least one of its values is non-empty.
"""


def _decorate_immunization(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Every thing related to the immunization object itself like status and identifier"""
    errors: List[TransformerFieldError] = []

    # Check that not_given value is valid
    not_given_is_valid = (not_given := Convert.boolean(record.get("not_given"))) in [True, False]
    if not not_given_is_valid:
        errors.append(TransformerFieldError(field="NOT_GIVEN", message="NOT_GIVEN is missing or is not a boolean"))

    # Check that action_flag value is valid
    action_flag_is_valid = Convert.to_lower(record.get("action_flag")) in ["new", "update"]
    if not action_flag_is_valid:
        # Note that an action_flag of 'delete' goes to the delete lambda and the decorators should not be called
        message = "ACTION_FLAG is missing or is not in the set 'new', 'update', 'delete'"
        errors.append(TransformerFieldError(field="ACTION_FLAG", message=message))

    # TODO: Confirm below mapping, and that action_flag of delete goes to delete endpoint
    # not_given and action_flag must be valid to allow FHIR status field to be populated. The following mapping applies:
    # * NOT_GIVEN is True & ACTION_FLAG is "new" or "update"<---> Status will be set to 'not-done'
    # * NOT_GIVEN is False & ACTION_FLAG is "new" or "update" <---> Status will be set to 'completed'
    if not_given_is_valid and action_flag_is_valid:
        imms["status"] = "not-done" if not_given is True else "completed"

    # statusReason
    Add.custom_item(
        imms,
        "statusReason",
        [
            reason_not_given_code := record.get("reason_not_given_code"),
            reason_not_given_term := record.get("reason_not_given_term"),
        ],
        {"coding": [Create.dictionary({"code": reason_not_given_code, "display": reason_not_given_term})]},
    )

    # reasonCode (note that this is reason for vaccination, which is different from statusReason)
    Add.custom_item(
        imms,
        "reasonCode",
        [indication_code := record.get("indication_code"), indication_term := record.get("indication_term")],
        [{"coding": [Create.dictionary({"code": indication_code, "display": indication_term})]}],
    )

    Add.item(imms, "recorded", record.get("recorded_date"), Convert.date)

    Add.list_of_dict(imms, "identifier", {"value": record.get("unique_id"), "system": record.get("unique_id_uri")})

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_patient(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'patient' object and append to 'contained' list"""
    errors: List[TransformerFieldError] = []

    patient_identifier_values = [
        nhs_number := record.get("nhs_number"),
        nhs_number_status_indicator_code := record.get("nhs_number_status_indicator_code"),
        nhs_number_status_indicator_description := record.get("nhs_number_status_indicator_description"),
    ]
    patient_values = [
        person_surname := record.get("person_surname"),
        person_forename := record.get("person_forename"),
        person_gender_code := record.get("person_gender_code"),
        person_dob := record.get("person_dob"),
        person_postcode := record.get("person_postcode"),
    ] + patient_identifier_values

    # Add patient if there is at least one non-empty patient value
    if any(_is_not_empty(value) for value in patient_values):

        # Set up patient
        internal_patient_id = "Patient1"
        imms["patient"] = {"reference": f"#{internal_patient_id}"}
        patient = {
            "id": internal_patient_id,
            "resourceType": "Patient",
        }

        Add.item(patient, "birthDate", person_dob, Convert.date)

        Add.item(patient, "gender", person_gender_code, Convert.gender_code)

        Add.list_of_dict(patient, "address", {"postalCode": person_postcode})

        # Add patient name if there is at least one non-empty patient name value
        if any(_is_not_empty(value) for value in [person_surname, person_forename]):
            patient["name"] = [{}]
            Add.item(patient["name"][0], "family", person_surname)
            Add.custom_item(patient["name"][0], "given", [person_forename], [person_forename])

        # Add patient identifier if there is at least one non-empty patient identifier value
        if any(_is_not_empty(value) for value in patient_identifier_values):
            patient["identifier"] = [{}]

            if _is_not_empty(nhs_number):
                patient["identifier"][0]["value"] = nhs_number
                patient["identifier"][0]["system"] = "https://fhir.nhs.uk/Id/nhs-number"

            # Add the extension if there is at least one non-empty extension value
            if any(
                _is_not_empty(value)
                for value in [nhs_number_status_indicator_code, nhs_number_status_indicator_description]
            ):
                patient["identifier"][0]["extension"] = [
                    Create.extension_item(
                        url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                        system="https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                        code=nhs_number_status_indicator_code,
                        display=nhs_number_status_indicator_description,
                    )
                ]

        imms["contained"].append(patient)

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccine(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccine refers to the physical vaccine product the manufacturer"""
    errors: List[TransformerFieldError] = []

    Add.snomed(imms, "vaccineCode", record.get("vaccine_product_code"), record.get("vaccine_product_term"))

    Add.dictionary(imms, "manufacturer", {"display": record.get("vaccine_manufacturer")})

    Add.item(imms, "expirationDate", record.get("expiry_date"), Convert.date)

    Add.item(imms, "lotNumber", record.get("batch_number"))

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccination(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccination refers to the actual administration of a vaccine to a patient"""
    errors: List[TransformerFieldError] = []

    vaccination_extension_values = [
        vaccination_procedure_code := record.get("vaccination_procedure_code"),
        vaccination_procedure_term := record.get("vaccination_procedure_term"),
        vaccination_situation_code := record.get("vaccination_situation_code"),
        vaccination_situation_term := record.get("vaccination_situation_term"),
    ]

    # Add extension item if at least one extension item value is non-empty
    if any(_is_not_empty(value) for value in vaccination_extension_values):
        imms["extension"] = []

        for code, term, code_for in [
            (vaccination_procedure_code, vaccination_procedure_term, "Procedure"),
            (vaccination_situation_code, vaccination_situation_term, "Situation"),
        ]:
            if any(_is_not_empty(value) for value in [code, term]):
                imms["extension"].append(
                    Create.extension_item(
                        url=f"https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-Vaccination{code_for}",
                        system="http://snomed.info/sct",
                        code=code,
                        display=term,
                    )
                )

    Add.item(imms, "occurrenceDateTime", record.get("date_and_time"), Convert.date_time)

    Add.item(imms, "primarySource", record.get("primary_source"), Convert.boolean)

    Add.dictionary(imms, "reportOrigin", {"text": record.get("report_origin")})

    Add.snomed(imms, "site", record.get("site_of_vaccination_code"), record.get("site_of_vaccination_term"))

    Add.snomed(imms, "route", record.get("route_of_vaccination_code"), record.get("route_of_vaccination_term"))

    dose_quantity_values = [
        dose_amount := record.get("dose_amount"),
        dose_unit_term := record.get("dose_unit_term"),
        dose_unit_code := record.get("dose_unit_code"),
    ]
    dose_quantity_dict = {
        "value": Convert.integer_or_decimal(dose_amount),
        "unit": dose_unit_term,
        "system": "http://unitsofmeasure.org",
        "code": dose_unit_code,
    }
    Add.custom_item(imms, "doseQuantity", dose_quantity_values, Create.dictionary(dose_quantity_dict))

    Add.list_of_dict(imms, "protocolApplied", {"doseNumberPositiveInt": Convert.integer(record.get("dose_sequence"))})

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_performer(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'practitioner' object and 'organization' and append them to the 'contained' list"""
    errors: List[TransformerFieldError] = []

    organization_values = [
        site_code_type_uri := record.get("site_code_type_uri"),
        site_code := record.get("site_code"),
        site_name := record.get("site_name"),
    ]
    practitioner_values = [
        performing_professional_body_reg_uri := record.get("performing_professional_body_reg_uri"),
        performing_professional_body_reg_code := record.get("performing_professional_body_reg_code"),
        performing_professional_surname := record.get("performing_professional_surname"),
        performing_professional_forename := record.get("performing_professional_forename"),
    ]
    peformer_values = organization_values + practitioner_values

    # Add performer if there is at least one non-empty performer value
    if any(_is_not_empty(value) for value in peformer_values):
        imms["performer"] = []

        # Add organization if there is at least one non-empty organization value
        if any(_is_not_empty(value) for value in organization_values):
            organization = {"actor": {"type": "Organization"}}

            Add.item(organization["actor"], "display", site_name)

            Add.dictionary(organization["actor"], "identifier", {"system": site_code_type_uri, "value": site_code})

            imms["performer"].append(organization)

        # Add practitioner if there is at least one practitioner value
        if any(_is_not_empty(value) for value in practitioner_values):

            # Set up the practitioner
            internal_practitioner_id = "Practitioner1"
            practitioner = {"resourceType": "Practitioner", "id": internal_practitioner_id}
            imms["performer"].append({"actor": {"reference": f"#{internal_practitioner_id}"}})

            Add.list_of_dict(
                practitioner,
                "identifier",
                {"value": performing_professional_body_reg_code, "system": performing_professional_body_reg_uri},
            )

            # Add practitioner name if there is at least one non-empty practitioner name value
            if any(
                _is_not_empty(value) for value in [performing_professional_surname, performing_professional_forename]
            ):
                practitioner["name"] = [{}]
                Add.item(practitioner["name"][0], "family", performing_professional_surname)
                Add.custom_item(
                    practitioner["name"][0],
                    "given",
                    [performing_professional_forename],
                    [performing_professional_forename],
                )

            imms["contained"].append(practitioner)

    Add.custom_item(
        imms,
        "location",
        [location_code := record.get("location_code"), location_code_type_uri := record.get("location_code_type_uri")],
        {
            "type": "Location",
            "identifier": Create.dictionary({"value": location_code, "system": location_code_type_uri}),
        },
    )

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_questionnaire(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'questionnaire' object and append items list"""
    errors: List[TransformerFieldError] = []

    questionnaire_values = [
        consent_for_treatment_code := record.get("consent_for_treatment_code"),
        consent_for_treatment_description := record.get("consent_for_treatment_description"),
        care_setting_type_code := record.get("care_setting_type_code"),
        care_setting_type_description := record.get("care_setting_type_description"),
        reduced_validation_code := record.get("reduce_validation_code"),
        reduced_validation_reason := record.get("reduce_validation_reason"),
        local_patient_uri := record.get("local_patient_uri"),
        local_patient_id := record.get("local_patient_id"),
        ip_address := record.get("ip_address"),
        user_id := record.get("user_id"),
        user_name := record.get("user_name"),
        user_email := record.get("user_email"),
        submitted_timestamp := record.get("submitted_timestamp"),
        sds_job_role_name := record.get("sds_job_role_name"),
    ]

    if any(_is_not_empty(value) for value in questionnaire_values):
        questionare = {
            "resourceType": "QuestionnaireResponse",
            "id": "QR1",
            "status": "completed",
        }
        items = []

        # TODO: Check if consent and care should have snomed uri (had one in original version of this code,
        # but note that there is an option of freetext for consent). Current implementation doesn't include snomed uri,
        # add it if necessary

        if any(_is_not_empty(value) for value in [consent_for_treatment_code, consent_for_treatment_description]):
            consent = Create.dictionary(
                {"code": consent_for_treatment_code, "display": consent_for_treatment_description}
            )
            _add_questionnaire_item_to_list(items, "Consent", {"valueCoding": consent})

        if any(_is_not_empty(value) for value in [care_setting_type_code, care_setting_type_description]):
            care_setting = Create.dictionary({"code": care_setting_type_code, "display": care_setting_type_description})
            _add_questionnaire_item_to_list(items, "CareSetting", {"valueCoding": care_setting})

        if _is_not_empty(reduced_validation_code):
            _add_questionnaire_item_to_list(
                items, "ReduceValidation", {"valueBoolean": Convert.boolean(reduced_validation_code)}
            )

        if any(_is_not_empty(value) for value in [local_patient_uri, local_patient_id]):
            local_patient = Create.dictionary({"system": local_patient_uri, "value": local_patient_id})
            _add_questionnaire_item_to_list(items, "LocalPatient", {"valueReference": {"identifier": local_patient}})

        if _is_not_empty(submitted_timestamp):
            _add_questionnaire_item_to_list(
                items, "SubmittedTimeStamp", {"valueDateTime": Convert.date_time(submitted_timestamp)}
            )

        for key, value in {
            "IpAddress": ip_address,
            "UserId": user_id,
            "UserName": user_name,
            "UserEmail": user_email,
            "PerformerSDSJobRole": sds_job_role_name,
            "ReduceValidationReason": reduced_validation_reason,
        }.items():
            if _is_not_empty(value):
                _add_questionnaire_item_to_list(items, key, {"valueString": value})

        questionare["item"] = items
        imms["contained"].append(questionare)

    func_name = inspect.currentframe().f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


all_decorators: List[ImmunizationDecorator] = [
    _decorate_immunization,
    _decorate_patient,
    _decorate_vaccine,
    _decorate_vaccination,
    _decorate_performer,
    _decorate_questionnaire,
]


def decorate(imms: dict, record: OrderedDict[str, str]):
    """Decorate the immunization object with the provided record"""
    errors = []
    for decorator in all_decorators:
        try:
            dec_err = decorator(imms, record)
            if dec_err:
                errors.append(dec_err)
        except Exception as e:
            raise TransformerUnhandledError(decorator_name=str(decorator)) from e

    if errors:
        raise TransformerRowError(errors=errors)
