from dataclasses import dataclass


@dataclass
class MeshImmunisationRecord:
    nhs_number: str
    person_forename: str
    person_surname: str


class MeshCsvContent:

    @staticmethod
    def parse_from_csv(content: str) -> [MeshImmunisationRecord]:
        return [MeshImmunisationRecord("", "", ""), MeshImmunisationRecord("", "", "")]
