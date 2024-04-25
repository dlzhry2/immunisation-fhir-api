from collections import OrderedDict
import inspect
from typing import List, Callable, Dict, Optional

from batch.errors import DecoratorError, TransformerFieldError, TransformerUnhandledError, TransformerRowError
from batch.utils import _is_not_empty, _add_questionnaire_item_to_list, Create, Add, Convert


ImmunizationDecorator = Callable[[Dict, OrderedDict[str, str]], Optional[DecoratorError]]
"""A decorator function (Callable) takes current immunization object and
validates it and adds appropriate fields to it. It returns None if no error occurs, otherwise it
returns an error object that has a list of all field errors. DO NOT raise any exception during this process.
The caller will catch Exception and treat them as unhandled errors. This way we can log these errors which are bugs or
a result of a batch file with unexpected headers/values.
NOTE: The decorators are order independent. They can be called in any order, so don't rely on previous changes.
NOTE: decorate function is the only public function. If you add a new decorator, call it in this function.
"""


def _decorate_immunization(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Every thing related to the immunization object itself like status and identifier"""
    errors: List[TransformerFieldError] = []

    # NOT_GIVEN and ACTION_FLAG must contain valid values to allow transformation
    if (not_given := Convert.boolean(record.get("not_given"))) not in [True, False]:
        errors.append(TransformerFieldError(field="NOT_GIVEN", message="NOT_GIVEN is missing or is not a boolean"))
    elif (action_flag := Convert.to_lower(record.get("action_flag"))) not in [
        "new",
        "update",
        "delete",
    ]:
        errors.append(
            TransformerFieldError(
                field="ACTION_FLAG", message="ACTION_FLAG is missing or is not in the set 'new', 'update', 'delete'"
            )
        )
    else:
        # Add status. The following mapping applies:
        # * NOT_GIVEN is True & ACTION_FLAG is "new" or "update" or "delete" <---> Status will be set to 'not-done'
        # * NOT_GIVEN is False & ACTION_FLAG is "new" or "update" <---> Status will be set to 'completed'
        # * NOT_GIVEN is False and ACTION_FLAG is "delete" <---> Status will be set to entered-in-error'
        if not_given is True:
            imms["status"] = "not-done"
        elif not_given is False:
            if action_flag == "new" or action_flag == "update":
                imms["status"] = "completed"
            elif action_flag == "delete":
                imms["status"] = "entered-in-error"

    # statusReason
    Add.custom_item(
        imms,
        "statusReason",
        [
            reason_not_given_code := record.get("reason_not_given_code"),
            reason_not_given_term := record.get("reason_not_given_term"),
        ],
        {"coding": [{"code": reason_not_given_code, "display": reason_not_given_term}]},
    )

    # reasonCode (note that this is reason for vaccination, which is different from statusReason)
    Add.custom_item(
        imms,
        "reasonCode",
        [indication_code := record.get("indication_code"), indication_term := record.get("indication_term")],
        [{"coding": [{"code": indication_code, "display": indication_term}]}],
    )

    Add.item(imms, "recorded", record.get("recorded_date"), Convert.date)

    Add.list_of_dict(imms, "identifier", {"value": record.get("unique_id"), "system": record.get("unique_id_uri")})

    func_name = inspect.currentframe().f_back.f_code.co_name
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

        Add.item(patient, "gender", person_gender_code, Convert.gender_code)

        Add.item(patient, "birthDate", person_dob, Convert.date)

        Add.list_of_dict(patient, "address", {"postalCode": person_postcode})

        Add.custom_item(
            patient, "name", [person_surname, person_forename], [{"family": person_surname, "given": [person_forename]}]
        )

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

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccine(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccine refers to the physical vaccine product the manufacturer"""
    errors: List[TransformerFieldError] = []

    Add.snomed(imms, "vaccineCode", record.get("vaccine_product_code"), record.get("vaccine_product_term"))

    Add.dict(imms, "manufacturer", {"display": record.get("vaccine_manufacturer")})

    Add.item(imms, "expirationDate", record.get("expiry_date"), Convert.date)

    Add.item(imms, "lotNumber", record.get("batch_number"))

    func_name = inspect.currentframe().f_back.f_code.co_name
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

    Add.dict(imms, "reportOrigin", {"text": record.get("report_origin")})

    Add.snomed(imms, "site", record.get("site_of_vaccination_code"), record.get("site_of_vaccination_term"))

    Add.snomed(imms, "route", record.get("route_of_vaccination_code"), record.get("route_of_vaccination_term"))

    dose_quantity_dict = {
        "value": Convert.decimal(record.get("dose_amount")),
        "unit": record.get("dose_unit_term"),
        "system": "http://unitsofmeasure.org",
        "code": record.get("dose_unit_code"),
    }
    Add.dict(imms, "doseQuantity", dose_quantity_dict)

    dose_sequence = Convert.integer(record.get("dose_sequence"))
    Add.custom_item(imms, "protocolApplied", [dose_sequence], [{"doseNumberPositiveInt": dose_sequence}])

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_performer(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'practitioner' object and 'organization' and append them to the 'contained' list"""
    errors: List[TransformerFieldError] = []

    organization_values = [
        site_code_type_uri := record.get("site_code_type_uri"),
        site_code := record.get("site_code"),
        # TODO: Confirm how to handle absent site_name. Currently defaulted to unkown if site_code exists in order
        # to pass validation. Note that site_name is not in vaccinations 4.1 spec, but is mandatory in FHIR API spec.
        site_name := record.get("site_name", "unknown") if site_code else record.get("site_name"),
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

            Add.dict(organization["actor"], "identifier", {"system": site_code_type_uri, "value": site_code})

            imms["performer"].append(organization)

        # Add practitioner if there is at least one practitioner value
        if any(_is_not_empty(value) for value in practitioner_values):

            # Set up the practitioner
            internal_practitioner_id = "practitioner1"
            practitioner = {"resourceType": "Practitioner", "id": internal_practitioner_id}
            imms["performer"].append({"actor": {"reference": f"#{internal_practitioner_id}"}})

            Add.list_of_dict(
                practitioner,
                "identifier",
                {"value": performing_professional_body_reg_code, "system": performing_professional_body_reg_uri},
            )

            Add.custom_item(
                practitioner,
                "name",
                [performing_professional_surname, performing_professional_forename],
                [{"family": performing_professional_surname, "given": [performing_professional_forename]}],
            )

            imms["contained"].append(practitioner)

    Add.custom_item(
        imms,
        "location",
        [location_code := record.get("location_code"), location_code_type_uri := record.get("location_code_type_uri")],
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

        # TODO: Check if consent and care should have snomed uri (had one in original version of this code,
        # but note that there is an option of freetext for consent). Current implementation doesn't include snomed uri,
        # add it if necessary

        if any(_is_not_empty(value) for value in [consent_for_treatment_code, consent_for_treatment_description]):
            consent = Create.dict({"code": consent_for_treatment_code, "display": consent_for_treatment_description})
            _add_questionnaire_item_to_list(items, "Consent", {"valueCoding": consent})

        if any(_is_not_empty(value) for value in [care_setting_type_code, care_setting_type_description]):
            care_setting = Create.dict({"code": care_setting_type_code, "display": care_setting_type_description})
            _add_questionnaire_item_to_list(items, "CareSetting", {"valueCoding": care_setting})

        if any(_is_not_empty(value) for value in [local_patient_uri, local_patient_id]):
            local_patient = Create.dict({"system": local_patient_uri, "value": local_patient_id})
            _add_questionnaire_item_to_list(items, "LocalPatient", {"valueReference": {"identifier": local_patient}})

        if _is_not_empty(reduced_validation_code):
            _add_questionnaire_item_to_list(
                items, "ReduceValidation", {"valueBoolean": Convert.boolean(reduced_validation_code)}
            )

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

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


all_decorators: List[ImmunizationDecorator] = [
    _decorate_immunization,
    _decorate_patient,
    _decorate_vaccine,
    _decorate_vaccination,
    _decorate_performer,
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
