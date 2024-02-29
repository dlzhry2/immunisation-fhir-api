from typing import Optional
import datetime


class SearchParams:
    nhs_number: str
    disease_types: list[str]
    date_from: Optional[datetime.date]

    def __init__(self,
                 nhs_number: str,
                 disease_type: list[str],
                 date_from: Optional[datetime.date]):
        self.nhs_number = nhs_number
        self.disease_types = disease_type
        self.date_from = date_from

    def __repr__(self):
        return str(self.__dict__)
