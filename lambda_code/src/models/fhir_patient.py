"""Patient FHIR R4B validator"""
from fhir.resources.R4B.patient import Patient
from models.nhs_validators import NHSValidators


class PatientValidator:
    """
    Validate the patient record against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self, json_data) -> None:
        self.json_data = json_data

    @classmethod
    def validate_person_dob(cls, values: dict) -> dict:
        """Validate Person DOB"""
        dob = values.get("birthDate")
        NHSValidators.validate_person_dob(str(dob))
        return values

    @classmethod
    def validate_person_gender_code(cls, values: dict) -> dict:
        """Validate Person Gender Code"""
        gender_code = values.get("gender")
        NHSValidators.validate_person_gender_code(gender_code)
        return values

    @classmethod
    def validate_person_postcode(cls, values: dict) -> dict:
        """Validate Person Postcode"""
        postcode = values.get("address")[0].postalCode
        NHSValidators.validate_person_postcode(postcode)
        return values

    def validate(self) -> Patient:
        """
        Add custom NHS validators to the Immunization model then generate the Immunization model
        from the JSON data
        """
        # Custom NHS validators
        Patient.add_root_validator(self.validate_person_dob)
        Patient.add_root_validator(self.validate_person_gender_code)
        Patient.add_root_validator(self.validate_person_postcode)

        # Generate the Patient model from the JSON data
        patient = Patient.parse_obj(self.json_data)

        return patient
