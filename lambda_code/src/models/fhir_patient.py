"""Patient FHIR R4B validator"""
from fhir.resources.R4B.patient import Patient
from models.nhs_validators import NHSPatientValidators


class PatientValidator:
    """
    Validate the patient record against the NHS specific validators and Immunization
    FHIR profile
    """

    def __init__(self, json_data) -> None:
        self.json_data = json_data

    @classmethod
    def validate_name_given(cls, values: dict) -> dict:
        """Validate given name (forename)"""
        name_given = values.get("name")[0].given[0]
        NHSPatientValidators.validate_name_given(name_given)
        return values

    @classmethod
    def validate_name_family(cls, values: dict) -> dict:
        """Validate family name (surname)"""
        name_family = values.get("name")[0].family
        NHSPatientValidators.validate_name_family(name_family)
        return values

    @classmethod
    def validate_birth_date(cls, values: dict) -> dict:
        """Validate birth date"""
        birth_date = values.get("birthDate")
        NHSPatientValidators.validate_birth_date(str(birth_date))
        return values

    @classmethod
    def validate_gender(cls, values: dict) -> dict:
        """Validate gender"""
        gender = values.get("gender")
        NHSPatientValidators.validate_gender(gender)
        return values

    @classmethod
    def validate_address_postal_code(cls, values: dict) -> dict:
        """Validate address postal code"""
        address_postal_code = values.get("address")[0].postalCode
        NHSPatientValidators.validate_address_postal_code(address_postal_code)
        return values

    def validate(self) -> Patient:
        """
        Add custom NHS validators to the Immunization model then generate the Immunization model
        from the JSON data
        """
        # Custom NHS validators
        Patient.add_root_validator(self.validate_birth_date)
        Patient.add_root_validator(self.validate_gender)
        Patient.add_root_validator(self.validate_address_postal_code)

        # Generate the Patient model from the JSON data
        patient = Patient.parse_obj(self.json_data)

        return patient
