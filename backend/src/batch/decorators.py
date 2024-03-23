from collections import OrderedDict

import inspect
from datetime import datetime
from typing import List, Callable, Dict, Optional

from batch.errors import DecoratorError, TransformerFieldError, TransformerUnhandledError, TransformerRowError
from mappings import vaccination_procedure_snomed_codes

ImmunizationDecorator = Callable[[Dict, OrderedDict[str, str]], Optional[DecoratorError]]
"""A decorator function (Callable) takes current immunization object and
validates it and adds appropriate fields to it. It returns None if no error occurs, otherwise it
returns an error object that has a list of all field errors. DO NOT raise any exception during this process.
The caller will catch Exception and treat them as unhandled errors. This way we can log these errors which are bugs or
a result of a batch file with unexpected headers/values.
NOTE: The decorators are order independent. They can be called in any order, so don't rely on previous changes.
NOTE: decorate function is the only public function. If you add a new decorator, call it in this function.
"""


def _make_snomed(code: str, display: str) -> dict:
    return {
        "system": "http://snomed.info/sct",
        "code": code,
        "display": "" if display is None else display
    }


# TODO NOT_GIVEN: constants.py for values, method: fhir_immunization_pre_validators.py pre_validate_status

def _convert_date_time(date_time: str) -> str:
    # TODO(validation): check the format in csv. Is conversion necessary?
    # TODO(validation): is conversion correct? do we have source code in the validation that does this?
    try:
        parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S00")
    except ValueError:
        parsed_dt = datetime.strptime(date_time, "%Y%m%dT%H%M%S")
    return parsed_dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _convert_gender_code(code: str) -> str:
    """Convert code to fhir gender, if we don't recognize the code, return the code as is"""
    code_to_fhir = {
        "1": "male",
        "2": "female",
        "9": "other",
        "0": "unknown"
    }
    return code_to_fhir.get(code, code)


def _parse_boolean(value: str) -> bool:
    """Boolean values are represented as string in the CSV file. This function converts them to Python boolean."""
    return value.lower() == "true"


def _decorate_status(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """ Takes ACTION_FLAG and NOT_GIVEN and sets the status accordingly. Status is a mandatory FHIR field.
    The following 1-to-1 mapping applies:
    * NOT_GIVEN is True <---> Status will be set to 'not-done' (and therefore ACTION_FLAG is
        absent)
    * NOT_GIVEN is False <---> Status will be set to 'completed' or 'entered-in-error' (and
        therefore ACTION_FLAG is present)
    """
    errors: List[TransformerFieldError] = []

    if not_given := record.get("not_given"):
        if _parse_boolean(not_given):
            imms["status"] = "not-done"
        else:
            if action_flag := record.get("action_flag"):
                if action_flag.lower() == "new":
                    imms["status"] = "completed"
                else:
                    imms["status"] = "entered-in-error"
            else:
                errors.append(TransformerFieldError(field="action_flag", message="Action flag is missing"))

    else:
        errors.append(TransformerFieldError(field="not_given", message="Not given is missing"))

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_patient(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'patient' object and append to 'contained' list"""
    errors: List[TransformerFieldError] = []

    def create_verified_nhs_number_extension(_code: str, _display: str) -> dict:
        return {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                        "code": _code,
                        "display": "" if _display is None else _display
                    }
                ]
            }
        }

    internal_id = "patient_1"
    imms["patient"] = {"reference": f"#{internal_id}"}
    patient = {
        "id": internal_id,
        "resourceType": "Patient",
        "identifier": [],
        "name": [],
    }

    if nhs_number := record.get("nhs_number"):
        identifier = {
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": nhs_number
        }
        if id_code := record.get("nhs_number_status_indicator_code"):
            id_display = record.get("nhs_number_status_indicator_description")
            extension = create_verified_nhs_number_extension(id_code, id_display)
            identifier["extension"] = [extension]

        patient["identifier"].append(identifier)

    person_surname = record.get("person_surname")
    person_forename = record.get("person_forename")
    if person_surname is not None and person_forename is not None:
        patient["name"].append({
            "family": person_surname,
            "given": [person_forename]
        })

    if person_dob := record.get("person_dob"):
        patient["birthDate"] = person_dob

    # TODO(validation): is it correct? should gender code be used like this?
    #  it should be converted to fhir
    # ‘male’ = 1
    # ‘female’ = 2
    # ‘other’ = 9
    # ‘unknown’ = 0
    if person_gender_code := record.get("person_gender_code"):
        gender = _convert_gender_code(person_gender_code)
        patient["gender"] = gender

    # TODO(validation): there is no address in the csv. Will it cause validation error?
    #  person_postcode
    imms["contained"].append(patient)

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccine(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccine refers to the physical vaccine product the manufacturer"""
    errors: List[TransformerFieldError] = []

    def create_vaccine_code(_vac_product_code: str, _display: str) -> dict:
        return {
            "coding": [_make_snomed(_vac_product_code, _display)]
        }

    if vac_product_code := record.get("vaccine_product_code"):
        display = record.get("vaccine_product_term")
        imms["vaccineCode"] = create_vaccine_code(vac_product_code, display)

    if manufacturer := record.get("vaccine_manufacturer"):
        imms["manufacturer"] = manufacturer

    # TODO(validation): is expiry refers to the product itself or something else?
    if expiry_date := record.get("expiry_date"):
        imms["expirationDate"] = expiry_date

    # TODO(validation): is it correct?
    if lot_number := record.get("batch_number"):
        imms["lotNumber"] = lot_number

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_vaccination(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Vaccination refers to the actual administration of a vaccine to a patient"""
    errors: List[TransformerFieldError] = []

    def create_vaccination_procedure_ext(_vaccine_type: str, _display: str) -> dict:
        return {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-VaccinationProcedureCode",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-VaccinationProcedureCode",
                        "code": _vaccine_type,
                        "display": "" if _display is None else _display
                    }
                ]
            }
        }

    if vac_code := record.get("vaccination_procedure_code"):
        if vac_type := vaccination_procedure_snomed_codes.get(vac_code):
            vac_display = record.get("vaccination_procedure_term")
            imms["extension"].append(create_vaccination_procedure_ext(vac_type, vac_display))

    # TODO(validation): what is RECORDED_DATE and should i use it here?
    if occurrenceDateTime := record.get("date_and_time"):
        imms["occurrenceDateTime"] = _convert_date_time(occurrenceDateTime)

    if primary_source := record.get("primary_source"):
        imms["primarySource"] = _parse_boolean(primary_source)

    if report_origin := record.get("report_origin"):
        imms["reportOrigin"] = report_origin

    # TODO(validation): there is also SITE_CODE in csv. What's that?
    if site_code := record.get("site_of_vaccination_code"):
        site_display = record.get("site_of_vaccination_term")
        imms["site"] = {
            "coding": [_make_snomed(site_code, site_display)]
        }
    if route_code := record.get("route_of_vaccination_code"):
        route_display = record.get("route_of_vaccination_term")
        imms["route"] = {
            "coding": [_make_snomed(route_code, route_display)]
        }

    dose_amount = record.get("dose_amount")
    dose_unit_code = record.get("dose_unit_code")
    dose_unit_term = record.get("dose_unit_term")
    # TODO(validation): should dose_unit_code be enforced?
    # TODO(validation): what to do with dose_sequence?
    if dose_amount is not None and dose_unit_code is not None:
        imms["doseQuantity"] = {
            "value": dose_amount,
            "unit": dose_unit_code,
            "system": "" if dose_unit_term is None else dose_unit_term
        }

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_practitioner(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'practitioner' object and 'organization' and append them to the 'contained' list"""
    errors: List[TransformerFieldError] = []

    # TODO(validation): is it correct?
    if prac_org := record.get("performing_professional_body_reg_code"):
        prac_org_uri = record.get("performing_professional_body_reg_uri")
        practitioner = {
            "resourceType": "Practitioner",
            "id": "practitioner_1",
            "identifier": [],
            "name": []
        }
        practitioner["identifier"].append({
            "system": "" if prac_org_uri is None else prac_org_uri,
            "value": prac_org
        })
        imms["performer"].append({"actor": {"reference": "#practitioner_1"}})
        imms["contained"].append(practitioner)

        prac_name = record.get("performing_professional_forename")
        prac_family = record.get("performing_professional_surname")
        if prac_name is not None or prac_family is not None:
            practitioner["name"].append({
                "family": prac_family,
                "given": [prac_name]
            })

    # TODO(validation): is it correct. Also check the location below?
    if org_code := record.get("location_code"):
        org_uri = record.get("location_code_type_uri")
        organization = {"resourceType": "Organization", "identifier": [{
            "system": "" if org_uri is None else org_uri,
            "value": org_code
        }]}
        imms["performer"].append({"actor": organization})

    # TODO(validation): I think this wrong. what's the difference between this and the actor location?
    if location_code := record.get("location_code"):
        system = record.get("location_code_type_uri")
        imms["location"] = {
            "identifier": {
                "value": location_code,
                "system": "" if system is None else system
            }}

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


def _decorate_questionare(imms: dict, record: OrderedDict[str, str]) -> Optional[DecoratorError]:
    """Create the 'questionnaire' object and append items list"""

    def _make_questionare_item(_name: str, _item: dict) -> dict:
        return {
            "linkId": _name,
            "answer": [_item]
        }

    errors: List[TransformerFieldError] = []

    questionare = {
        "resourceType": "QuestionnaireResponse",
        # TODO(validation): what is this ID?
        "id": "QR1",
        "status": "completed",
    }
    items = []

    # TODO(validation): where is reduced validation?
    # TODO(validation): I our example's questionare.
    #  Is there anything in csv that i missed adding to questionare?

    if ip_address := record.get("ip_address"):
        items.append(_make_questionare_item("IpAddress", {"valueString": ip_address}))

    if consent_code := record.get("consent_for_treatment_code"):
        item = _make_snomed(consent_code, record.get("consent_for_treatment_description"))
        items.append(_make_questionare_item("Consent", {"valueCoding": item}))

    if care_code := record.get("care_setting_type_code"):
        item = _make_snomed(care_code, record.get("care_setting_type_description"))
        items.append(_make_questionare_item("CareSetting", {"valueCoding": item}))

    if local_patient_id := record.get("local_patient_id"):
        system = record.get("local_patient_uri")
        reference = {
            "valueReference": {
                "identifier": {
                    "system": system,
                    "value": local_patient_id
                }
            }
        }
        items.append(_make_questionare_item("LocalPatient", reference))

    if user_id := record.get("user_id"):
        items.append(_make_questionare_item("UserId", {"valueString": user_id}))
    if user_name := record.get("user_name"):
        items.append(_make_questionare_item("UserName", {"valueString": user_name}))
    if user_email := record.get("user_email"):
        items.append(_make_questionare_item("UserEmail", {"valueString": user_email}))

    if submitted_timestamp := record.get("submitted_timestamp"):
        # TODO(validation): check the format in csv. Is conversion necessary?
        converted_dt = _convert_date_time(submitted_timestamp)

        items.append(_make_questionare_item("SubmittedTimeStamp", {"valueDateTime": converted_dt}))

    if sds_job_role := record.get("sds_job_role_name"):
        items.append(_make_questionare_item("PerformerSDSJobRole", {"valueString": sds_job_role}))

    if len(items) > 0:
        questionare["item"] = items
        imms["contained"].append(questionare)

    func_name = inspect.currentframe().f_back.f_code.co_name
    return DecoratorError(errors=errors, decorator_name=func_name) if errors else None


all_decorators: List[ImmunizationDecorator] = [
    _decorate_status,
    _decorate_patient,
    _decorate_vaccine,
    _decorate_vaccination,
    _decorate_practitioner,
    _decorate_questionare
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
