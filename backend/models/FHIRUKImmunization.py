from fhir.resources.immunization import Immunization as FHIRImmunization
from fhir.resources.bundle import Bundle


class UKFHIRImmunization:
    def __init__(self, *args, **kwargs):

        self.immunization: FHIRImmunization = None
        self.bundle = Bundle(
            resource_type="Bundle",
            type="transaction",  # Adjust the type as needed (e.g., "transaction", "batch", etc.)
            entry=[],
        )

    def get_bundle(self):
        return self.bundle.json()
    
    def add_patient_to_bundle(self, entry):
        self.bundle.entry.append({"patient": entry})

    def add_performer_to_bundle(self, entry):
        self.bundle.entry.append({"performer": {"actor": entry}})

    def add_manufacturer_to_bundle(self, entry):
        self.bundle.entry.append({"manufacturer": entry})

    def add_report_origin_to_bundle(self, entry):
        self.bundle.entry.append({"reportOrigin": entry})

    def add_reason_code_to_bundle(self, entry):
        self.bundle.entry.append({"reasonCode": entry})

    def add_recorded_to_bundle(self, entry):
        recorded = {"recorded": entry}
        self.bundle.entry.append(recorded)

    def add_immunization_to_bundle(self, entry):
        self.bundle.entry.append(entry)
