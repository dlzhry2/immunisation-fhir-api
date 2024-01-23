"""Dictionary of vaccine procedure snomed codes and their mapping to vaccine type"""

# TODO: Update dictionary to use correct codes and mappings once received from Imms team
vaccination_procedure_snomed_codes = {
    "1324681000000101": "COVID-19",
    "1324691000000104": "COVID-19",
    "1324671000000103": "COVID-19",
    "1362591000000103": "COVID-19",
    "1363861000000103": "COVID-19",
    "1363791000000101": "COVID-19",
    "1363831000000108": "COVID-19",
    "mockFLUcode1": "FLU",
    "mockFLUcode2": "FLU",
    "mockHPVcode1": "HPV",
    "mockHPVcode2": "HPV",
    "mockMMRcode1": "MMR",
    "mockMMRcode2": "MMR",
    "mockOTHERDISEASEcode1": "OTHER_DISEASE",
    "mockMENINGITIScode1": "MEN",
}

# TODO: Update dictionary to use correct codes and mappings.
# This is just an example of a possible structure
vaccine_type_applicable_validations = {
    "patient_identifier_value": {
        "COVID-19": "R",
        "FLU": "R",
        "HPV": "R",
        "MMR": "R",
    },
    "occurrence_date_time": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "site_code_code": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "site_name_code": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "identifier_value": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "identifier_system": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "recorded": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "primary_source": {
        "COVID-19": "M",
        "FLU": "M",
        "HPV": "M",
        "MMR": "M",
    },
    "report_origin_text": {
        "COVID-19": "CM",
        "FLU": "CM",
        "HPV": "CM",
        "MMR": "CM",
    },
}
