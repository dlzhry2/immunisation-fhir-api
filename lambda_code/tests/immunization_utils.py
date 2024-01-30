import json

from fhir.resources.R4B.immunization import Immunization

valid_nhs_number = "2374658346"


def create_an_immunization(imms_id, nhs_number=valid_nhs_number) -> Immunization:
    base_imms = {
        "resourceType": "Immunization",
        "id": imms_id,
        "identifier": [
            {
                "system": "https://supplierABC/ODSCode",
                "value": imms_id
            }
        ],
        "status": "completed",
        "occurrenceDateTime": "2020-12-14T10:08:15+00:00",
        "patient": {
            "reference": "urn:uuid:124fcb63-669c-4a3c-af2b-caf55de167ec",
            "type": "Patient",
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/nhs-number",
                "value": nhs_number
            }
        },
        "vaccineCode": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "39114911000001105",
                "display": "some text"
            }]
        },
    }
    return Immunization.parse_obj(base_imms)


def create_an_immunization_dict(imms_id, nhs_number=valid_nhs_number):
    imms = create_an_immunization(imms_id, nhs_number)
    # Convert FHIR OrderedDict to Dict by first converting it to json and then load it again
    return json.loads(imms.json())
