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
        """Pre-validate name"""
        try:
            name = values["name"]
            PatientPreValidators.name(name)
        except KeyError:
            pass

        return values

    def add_custom_root_validators(self):
        """Add custom NHS validators to the model"""
        Patient.add_root_validator(self.pre_validate_name, pre=True)

    def validate(self, json_data) -> Patient:
        """Generate the Patient model from the JSON data"""
        return Patient.parse_obj(json_data)
