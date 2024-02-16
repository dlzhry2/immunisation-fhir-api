"""Dictionary of vaccine procedure snomed codes and their mapping to vaccine type"""

from dataclasses import dataclass


@dataclass
class DiseaseTypes:
    """
    Disease types
    """

    covid_19: str = "COVID19"
    flu: str = "FLU"
    hpv: str = "HPV"
    mmr: str = "MMR"


@dataclass
class Mandation:
    """Mandation types"""

    mandatory: str = "M"
    conditional_mandatory: str = "CM"
    required: str = "R"
    optional: str = "O"
    not_applicable: str = "N/A"


# TODO: Update dictionary to use correct codes and mappings once received from Imms team
# Dictionary of vaccine procedure snomed codes and their mapping to vaccine type. Any new codes
# should be added here
vaccination_procedure_snomed_codes = {
    "1324681000000101": DiseaseTypes.covid_19,
    "1324691000000104": DiseaseTypes.covid_19,
    "1324671000000103": DiseaseTypes.covid_19,
    "1362591000000103": DiseaseTypes.covid_19,
    "1363861000000103": DiseaseTypes.covid_19,
    "1363791000000101": DiseaseTypes.covid_19,
    "1363831000000108": DiseaseTypes.covid_19,
    "822851000000102": DiseaseTypes.flu,  # TODO: remove this code if necessary once full list of
    # accceptable codes is received (note that it has been copied from the sample data, to allow
    # the sample flu data to pass the validator)
    "mockFLUcode1": DiseaseTypes.flu,
    "mockFLUcode2": DiseaseTypes.flu,
    "mockHPVcode1": DiseaseTypes.hpv,
    "mockHPVcode2": DiseaseTypes.hpv,
    "mockMMRcode1": DiseaseTypes.mmr,
    "mockMMRcode2": DiseaseTypes.mmr,
    "mockOTHERDISEASEcode1": "OTHER_DISEASE",
    "mockMENINGITIScode1": "MEN",
}

# Dictionary of vaccine types and their applicable mandations for each field
vaccine_type_applicable_validations = {
    "patient_identifier_value": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "patient_name_given": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "patient_name_family": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "patient_birth_date": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "patient_gender": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "patient_address_postal_code": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "occurrence_date_time": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "organization_identifier_value": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "organization_display": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "identifier_value": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "identifier_system": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "practitioner_name_given": {
        DiseaseTypes.covid_19: Mandation.optional,
        DiseaseTypes.flu: Mandation.optional,
        DiseaseTypes.hpv: Mandation.optional,
        DiseaseTypes.mmr: Mandation.optional,
    },
    "practitioner_name_family": {
        DiseaseTypes.covid_19: Mandation.optional,
        DiseaseTypes.flu: Mandation.optional,
        DiseaseTypes.hpv: Mandation.optional,
        DiseaseTypes.mmr: Mandation.optional,
    },
    "practitioner_identifier_value": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.optional,
        DiseaseTypes.mmr: Mandation.optional,
    },
    "practitioner_identifier_system": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.optional,
        DiseaseTypes.mmr: Mandation.optional,
    },
    "performer_sds_job_role": {
        DiseaseTypes.covid_19: Mandation.optional,
        DiseaseTypes.flu: Mandation.optional,
        DiseaseTypes.hpv: Mandation.optional,
        DiseaseTypes.mmr: Mandation.optional,
    },
    "recorded": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "primary_source": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "report_origin_text": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.conditional_mandatory,
        DiseaseTypes.mmr: Mandation.conditional_mandatory,
    },
    "vaccination_procedure_term": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "vaccination_situation_code": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.conditional_mandatory,
        DiseaseTypes.mmr: Mandation.conditional_mandatory,
    },
    "vaccination_situation_term": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "status_reason_coding_code": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.conditional_mandatory,
        DiseaseTypes.mmr: Mandation.conditional_mandatory,
    },
    "status_reason_coding_display": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "protocol_applied_dose_number_positive_int": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "vaccine_code_coding_code": {
        DiseaseTypes.covid_19: Mandation.mandatory,
        DiseaseTypes.flu: Mandation.mandatory,
        DiseaseTypes.hpv: Mandation.mandatory,
        DiseaseTypes.mmr: Mandation.mandatory,
    },
    "vaccine_code_coding_display": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "manufacturer_display": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "lot_number": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "expiration_date": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "site_coding_code": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "site_coding_display": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "route_coding_code": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "route_coding_display": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "dose_quantity_value": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "dose_quantity_code": {
        DiseaseTypes.covid_19: Mandation.conditional_mandatory,
        DiseaseTypes.flu: Mandation.conditional_mandatory,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "dose_quantity_unit": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "reason_code_coding_code": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
    "reason_code_coding_display": {
        DiseaseTypes.covid_19: Mandation.required,
        DiseaseTypes.flu: Mandation.required,
        DiseaseTypes.hpv: Mandation.required,
        DiseaseTypes.mmr: Mandation.required,
    },
}
