"""Patient FHIR R4B validator"""
from fhir.resources.R4B.patient import Patient
from models.patient_pre_validators import PatientPreValidators


class PatientValidator:
    """
    Validate the patient record against the NHS specific validators and Patient
    FHIR profile
    """

    def __init__(self) -> None:
        pass

    @classmethod
    def pre_validate_name(cls, values: dict) -> dict:
        """Pre-validate that name is an array of length 1 (if it exists)"""
        try:
            name = values["name"]
            PatientPreValidators.name(name)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_name_given(cls, values: dict) -> dict:
        """
        Pre-validate that name -> given (patient forename) is a non-empty array of non-empty
        strings (if it exists)
        """
        try:
            name_given = values["name"][0]["given"]
            PatientPreValidators.name_given(name_given)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_name_family(cls, values: dict) -> dict:
        """Pre-validate that name -> family is a non-empty string (if it exists)"""

        try:
            name_family = values["name"][0]["family"]
            PatientPreValidators.name_family(name_family)
        except KeyError:
            pass

        return values

    @classmethod
    def pre_validate_birth_date(cls, values: dict) -> dict:
        """
        Pre-validate that birthDate (person DOB) is a string in the format YYYY-MM-DD, where MM
        represents a number between from 01 to 12, and DD respresents a number from 01 to 31
        """

        try:
            birth_date = values["birthDate"]
            PatientPreValidators.birth_date(birth_date)
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Patient.add_root_validator(self.pre_validate_name, pre=True)
        Patient.add_root_validator(self.pre_validate_name_given, pre=True)
        Patient.add_root_validator(self.pre_validate_name_family, pre=True)
        Patient.add_root_validator(self.pre_validate_birth_date, pre=True)

    def validate(self, json_data) -> Patient:
        """Generate the Patient model from the JSON data"""
        return Patient.parse_obj(json_data)
