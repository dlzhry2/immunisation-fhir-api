from collections import OrderedDict

import inspect
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import List, Callable, Dict, Optional

from batch.errors import DecoratorError, TransformerFieldError, TransformerUnhandledError, TransformerRowError

ImmunizationDecorator = Callable[[Dict, OrderedDict[str, str]], Optional[DecoratorError]]
"""A decorator function (Callable) takes current immunization object and
validates it and adds appropriate fields to it. It returns None if no error occurs, otherwise it
returns an error object that has a list of all field errors. DO NOT raise any exception during this process.
The caller will catch Exception and treat them as unhandled errors. This way we can log these errors which are bugs or
a result of a batch file with unexpected headers/values.
NOTE: The decorators are order independent. They can be called in any order, so don't rely on previous changes.
NOTE: decorate function is the only public function. If you add a new decorator, call it in this function.
"""

snomed_url = "http://snomed.info/sct"


def _is_not_empty(value: any) -> bool:
    """Determine if a value is not empty i.e. there is data present. Note that some
    "Falsey" values, such as zero values and a boolean of false, are valid data"""
    return value not in [None, "", [], {}, (), [""]]


def _make_snomed(code: str, display: str) -> dict:
    return {"system": "http://snomed.info/sct", "code": code, "display": display}


def _make_dict(fields: dict) -> dict:
    """Makes a dictionary with all empty items removed"""
    dictionary = {}
    for fhir_key_name, field_value in fields.items():
        if _is_not_empty(field_value):
            dictionary[fhir_key_name] = field_value
    return dictionary


def _make_extension_item(url: str, system: str, code: str, display: str) -> dict:
    return {
        "url": url,
        "valueCodeableConcept": {"coding": [{"system": system, "code": code, "display": display}]},
    }


def _add_item(dictionary: dict, fhir_field_name: str, value: any, conversion_fn=None):
    if _is_not_empty(value):
        dictionary[fhir_field_name] = value if conversion_fn is None else conversion_fn(value)


def _add_dict(dictionary: dict, fhir_field_name: str, fields: dict):
    if any(_is_not_empty(field_value) for field_value in fields.values()):
        _add_item(dictionary, fhir_field_name, _make_dict(fields))


def _add_list_of_dict(dictionary: dict, fhir_field_name: str, fields: dict):
    if any(_is_not_empty(field_value) for field_value in fields.values()):
        _add_item(dictionary, fhir_field_name, [_make_dict(fields)])


def _add_custom_item(dictionary: dict, fhir_field_name: str, field_values: list, item_to_add: any):
    if any(_is_not_empty(field_value) for field_value in field_values):
        dictionary[fhir_field_name] = item_to_add


def _add_snomed(dictionary: dict, fhir_field_name: str, code: str, display: str):
    if _is_not_empty(code) or _is_not_empty(display):
        dictionary[fhir_field_name] = {"coding": [_make_dict({"system": snomed_url, "code": code, "display": display})]}


def _add_questionnaire_item(items: list, linkId: str, item: dict):
    # TODO: Need to unit test this function
    items.append({"linkId": linkId, "answer": [item]})


def _convert_date_time(date_time: str) -> str:
    try:
        parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S00")
    except ValueError:
        parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S")
    return parsed_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _convert_date(date: str) -> str:
    return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")


def _convert_gender_code(code: str) -> str:
    """Convert code to fhir gender, if we don't recognize the code, return the code as is"""
    code_to_fhir = {"1": "male", "2": "female", "9": "other", "0": "unknown"}
    return code_to_fhir.get(code, code)


def _convert_decimal(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal(".0001"), rounding=ROUND_DOWN)


def _parse_boolean(value: str) -> bool:
    """Boolean values are represented as string in the CSV file. This function converts them to Python boolean."""
    return value.lower() == "true"


def _parse_boolean2(value: str) -> bool:
    """Booleans are represented as strings in the CSV. This function converts them to Python booleans where possible"""
    lower_value = value.lower() if isinstance(value, str) else None
    return {"true": True, "false": False}.get(lower_value, value)


def _decorate_immunization(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Every thing related to the immunization object itself like status and identifier
    Takes ACTION_FLAG and NOT_GIVEN and sets the status accordingly. Status is a mandatory FHIR field.
    The following 1-to-1 mapping applies:
    * NOT_GIVEN is True <---> Status will be set to 'not-done' (and therefore ACTION_FLAG is
        absent)
    * NOT_GIVEN is False <---> Status will be set to 'completed' or 'entered-in-error' (and
        therefore ACTION_FLAG is present)
    """
    errors: List[TransformerFieldError] = []

    # NOT_GIVEN and ACTION_FLAG must contain valid values to allow transformation
    if (not_given := _parse_boolean2(record.get("not_given"))) not in [True, False]:
        errors.append(TransformerFieldError(field="NOT_GIVEN", message="NOT_GIVEN is missing or is not a boolean"))

    if not isinstance(action_flag := record.get("action_flag"), str) or (action_flag.lower()) not in [
        "new",
        "update",
        "delete",
    ]:
        errors.append(
            TransformerFieldError(
                field="ACTION_FLAG", message="ACTION_FLAG is missing or is not in the set 'new', 'update', 'delete'"
            )
        )

    # TODO: Find this comment in validators and update logic
    # Add status. The following mapping applies:
    # * NOT_GIVEN is True <---> Status will be set to 'not-done' (irrespective of the ACTION_FLAG value)
    # * NOT_GIVEN is False & ACTION_FLAG is "new" or "update" <---> Status will be set to 'completed'
    # * NOT_GIVEN is False and ACTION_FLAG is "delete" <---> Status will be set to entered-in-error'
    if not_given is True:
        imms["status"] = "not-done"
    elif not_given is False:
        # TODO: Check with IMMS team r.e. status when action_flag is "update"
        if action_flag == "new" or action_flag == "update":
            imms["status"] = "completed"
        elif action_flag == "delete":
            imms["status"] = "entered-in-error"

    # statusReason
    reason_not_given_code = record.get("reason_not_given_code")
    reason_not_given_term = record.get("reason_not_given_term")
    if _is_not_empty(reason_not_given_code) or _is_not_empty(reason_not_given_term):
        imms["statusReason"] = {"coding": [{"code": reason_not_given_code, "display": reason_not_given_term}]}

    # reasonCode
    indication_code = record.get("indication_code")
    indication_term = record.get("indication_term")
    if _is_not_empty(indication_code) or _is_not_empty(indication_term):
        imms["reasonCode"] = [{"coding": [{"code": indication_code, "display": indication_term}]}]

    # TODO: Confirm date expected format as differs between spec and 4.1 (files follow 4.1)
    _add_item(imms, "recorded", record.get("recorded_date"), _convert_date)

    _add_list_of_dict(imms, "identifier", {"value": record.get("unique_id"), "system": record.get("unique_id_uri")})

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_patient(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'patient' object and append to 'contained' list"""
    errors: List[TransformerFieldError] = []

    nhs_number_status_indicator_code = record.get("nhs_number_status_indicator_code")
    nhs_number_status_indicator_description = record.get("nhs_number_status_indicator_description")
    nhs_number = record.get("nhs_number")
    person_surname = record.get("person_surname")
    person_forename = record.get("person_forename")
    person_gender_code = record.get("person_gender_code")
    person_dob = record.get("person_dob")
    person_postcode = record.get("person_postcode")

    patient_extension_values = [nhs_number_status_indicator_code, nhs_number_status_indicator_description]
    patient_identifier_values = [nhs_number] + patient_extension_values
    patient_name_values = [person_surname, person_forename]
    patient_top_level_values = [person_gender_code, person_dob, person_postcode]
    patient_values = patient_top_level_values + patient_name_values + patient_identifier_values

    # Add patient if there is at least one non-empty patient value
    if any(_is_not_empty(value) for value in patient_values):
        internal_patient_id = "Patient1"
        imms["patient"] = {"reference": f"#{internal_patient_id}"}
        patient = {
            "id": internal_patient_id,
            "resourceType": "Patient",
        }

        _add_item(patient, "gender", person_gender_code, _convert_gender_code)

        _add_item(patient, "birthDate", person_dob, _convert_date)

        _add_list_of_dict(patient, "address", {"postalCode": person_postcode})

        # Add patient name if there is at least one non-empty patient name value
        if any(_is_not_empty(value) for value in patient_name_values):
            patient["name"] = [{}]

            _add_item(patient["name"][0], "family", person_surname)

            _add_custom_item(patient["name"][0], "given", [person_forename], [person_forename])

        # Add patient identifier if there is at least one non-empty patient identifier value
        if any(_is_not_empty(value) for value in patient_identifier_values):
            _add_list_of_dict(
                patient,
                "identifier",
                {"value": nhs_number, "system": "https://fhir.nhs.uk/Id/nhs-number"},
            )

            # Add the extension if there is at least one non-empty extension value
            if any(_is_not_empty(value) for value in patient_extension_values):
                extension_item = _make_extension_item(
                    url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                    system="https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                    code=nhs_number_status_indicator_code,
                    display=nhs_number_status_indicator_description,
                )
                patient["identifier"][0]["extension"] = [extension_item]

    imms["contained"].append(patient)

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccine(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccine refers to the physical vaccine product the manufacturer"""
    errors: List[TransformerFieldError] = []

    _add_snomed(imms, "vaccineCode", record.get("vaccine_product_code"), record.get("vaccine_product_term"))

    _add_dict(imms, "manufacturer", {"display": record.get("vaccine_manufacturer")})

    _add_item(imms, "expirationDate", record.get("expiry_date"), _convert_date)

    _add_item(imms, "lotNumber", record.get("batch_number"))

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccination(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccination refers to the actual administration of a vaccine to a patient"""
    errors: List[TransformerFieldError] = []

    vaccination_procedure_values = [
        vaccination_procedure_code := record.get("vaccination_procedure_code"),
        vaccination_procedure_term := record.get("vaccination_procedure_term"),
    ]

    vaccination_situation_values = [
        vaccination_situation_code := record.get("vaccination_situation_code"),
        vaccination_situation_term := record.get("vaccination_situation_term"),
    ]

    # Add extension item if at least one extension item value is non-empty
    if any(_is_not_empty(value) for value in vaccination_procedure_values + vaccination_situation_values):
        imms["extension"] = []

        if _is_not_empty(vaccination_procedure_code) or _is_not_empty(vaccination_procedure_term):
            imms["extension"].append(
                _make_extension_item(
                    url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedure",
                    system=snomed_url,
                    code=vaccination_procedure_code,
                    display=vaccination_procedure_term,
                )
            )

        if _is_not_empty(vaccination_situation_code) or _is_not_empty(vaccination_situation_term):
            imms["extension"].append(
                _make_extension_item(
                    url="https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationSituation",
                    system=snomed_url,
                    code=vaccination_situation_code,
                    display=vaccination_situation_term,
                )
            )

    _add_item(imms, "occurrenceDateTime", record.get("date_and_time"), _convert_date_time)

    _add_item(imms, "primarySource", record.get("primary_source"), _parse_boolean)

    _add_dict(imms, "reportOrigin", {"text": record.get("report_origin")})

    _add_snomed(imms, "site", record.get("site_of_vaccination_code"), record.get("site_of_vaccination_term"))

    _add_snomed(imms, "route", record.get("route_of_vaccination_code"), record.get("route_of_vaccination_term"))

    # dose_amount = record.get("dose_amount")
    # dose_unit_code = record.get("dose_unit_code")
    # dose_unit_term = record.get("dose_unit_term")
    # if dose_amount is not None and dose_unit_code is not None: # TODO: What is this logic for?
    #     imms["doseQuantity"] = {
    #         "value": float(_convert_decimal(dose_amount)),
    #         "code": dose_unit_code,
    #         "unit": dose_unit_term,
    #         "system": "http://unitsofmeasure.org",
    #     }

    # TODO: Move this to conversion function
    dose_amount = record.get("dose_amount")
    try:
        dose_amount = Decimal(dose_amount)
    except TypeError:
        pass

    dose_quantity_dict = {
        "value": dose_amount,  # Need to convert to decimal
        "unit": record.get("dose_unit_term"),
        "system": "http://unitsofmeasure.org",
        "code": record.get("dose_unit_code"),
    }
    _add_dict(imms, "doseQuantity", dose_quantity_dict)

    # TODO: Need to create a conversion function and handle non-numeric string
    if isinstance(dose_sequence := record.get("dose_sequence"), str):
        _add_custom_item(imms, "protocolApplied", [dose_sequence], [{"doseNumberPositiveInt": int(dose_sequence)}])

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_practitioner(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'practitioner' object and 'organization' and append them to the 'contained' list"""
    errors: List[TransformerFieldError] = []

    site_code_type_uri = record.get("site_code_type_uri")
    site_code = record.get("site_code")
    site_name = record.get("site_name")
    performing_professional_body_reg_uri = record.get("performing_professional_body_reg_uri")
    performing_professional_body_reg_code = record.get("performing_professional_body_reg_code")
    performing_professional_surname = record.get("performing_professional_surname")
    performing_professional_forename = record.get("performing_professional_forename")

    organization_identifier_values = [site_code_type_uri, site_code]
    organization_values = [site_name] + organization_identifier_values
    practitioner_identifier_values = [performing_professional_body_reg_uri, performing_professional_body_reg_code]
    practitioner_name_values = [performing_professional_surname, performing_professional_forename]
    practitioner_values = practitioner_name_values + practitioner_identifier_values
    peformer_values = organization_values + practitioner_name_values + practitioner_identifier_values

    # Add performer if there is at least one non-empty performer value
    if any(_is_not_empty(value) for value in peformer_values):
        imms["performer"] = []

        # Add actor if there is at least one non-empty organization value
        if any(_is_not_empty(value) for value in organization_values):
            organization = {"actor": {"type": "Organization"}}

            _add_item(organization["actor"], "display", site_name)

            if any(_is_not_empty(value) for value in organization_identifier_values):
                _add_dict(organization["actor"], "identifier", {"system": site_code_type_uri, "value": site_code})
            # TODO(validation): site_name is not mandatory in the csv, but it's mandatory in our api. Check handling.
            imms["performer"].append(organization)

        if any(_is_not_empty(value) for value in practitioner_values):
            internal_practitioner_id = "practitioner1"
            practitioner = {"resourceType": "Practitioner", "id": internal_practitioner_id}
            imms["performer"].append({"actor": {"reference": f"#{internal_practitioner_id}"}})

            # Add practitioner identifier if there is at least one non-empty patient identifier value
            if any(_is_not_empty(value) for value in practitioner_identifier_values):
                _add_list_of_dict(
                    practitioner,
                    "identifier",
                    {"value": performing_professional_body_reg_code, "system": performing_professional_body_reg_uri},
                )

            # Add practitioner name if there is at least one non-empty patient name value
            if any(_is_not_empty(value) for value in practitioner_name_values):
                practitioner["name"] = [{}]

                _add_item(practitioner["name"][0], "family", performing_professional_surname)

                _add_custom_item(
                    practitioner["name"][0],
                    "given",
                    [performing_professional_forename],
                    [performing_professional_forename],
                )

            imms["contained"].append(practitioner)

    location_code = record.get("location_code")
    location_code_type_uri = record.get("location_code_type_uri")
    _add_custom_item(
        imms,
        "location",
        [location_code, location_code_type_uri],
        {"type": "Location", "identifier": {"value": location_code, "system": location_code_type_uri}},
    )

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_questionare(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
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

        # TODO: Check if consent and care should have snomed uri (had one in original version of this code)

        if any(_is_not_empty(value) for value in [consent_for_treatment_code, consent_for_treatment_description]):
            consent = _make_dict({"code": consent_for_treatment_code, "display": consent_for_treatment_description})
            _add_questionnaire_item(items, "Consent", {"valueCoding": consent})

        if any(_is_not_empty(value) for value in [care_setting_type_code, care_setting_type_description]):
            care_setting = _make_dict({"code": care_setting_type_code, "display": care_setting_type_description})
            _add_questionnaire_item(items, "CareSetting", {"valueCoding": care_setting})

        if any(_is_not_empty(value) for value in [local_patient_uri, local_patient_id]):
            local_patient = _make_dict({"system": local_patient_uri, "value": local_patient_id})
            _add_questionnaire_item(items, "LocalPatient", {"valueReference": {"identifier": local_patient}})

        if _is_not_empty(reduced_validation_code):
            _add_questionnaire_item(
                items, "ReduceValidation", {"valueBoolean": _parse_boolean(reduced_validation_code)}
            )

        if _is_not_empty(submitted_timestamp):
            _add_questionnaire_item(
                items, "SubmittedTimeStamp", {"valueDateTime": _convert_date_time(submitted_timestamp)}
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
                _add_questionnaire_item(items, key, {"valueString": value})

        questionare["item"] = items
        imms["contained"].append(questionare)

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


all_decorators: List[ImmunizationDecorator] = [
    _decorate_immunization,
    _decorate_patient,
    _decorate_vaccine,
    _decorate_vaccination,
    _decorate_practitioner,
    _decorate_questionare,
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
