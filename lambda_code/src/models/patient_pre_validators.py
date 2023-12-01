"""Pre-validators for Patient model"""


class PatientPreValidators:
    """Pre-validators for Patient model"""

    @staticmethod
    def name(name: list[dict]) -> list[dict]:
        """Pre-validate name"""

        if not isinstance(name, list):
            raise TypeError("name must be an array")

        if len(name) != 1:
            raise ValueError("name must be an array of length 1")

        return name

    @staticmethod
    def name_given(name_given: list[str]) -> list[str]:
        """Pre-validate name given"""

        if not isinstance(name_given, list):
            raise TypeError("name -> given must be an array")

        if len(name_given) == 0:
            raise ValueError("name -> given must be a non-empty array")

        for name in name_given:
            if not isinstance(name, str):
                raise TypeError("name -> given must be an array of strings")

            if len(name) == 0:
                raise ValueError("name -> given must be an array of non-empty strings")

        return name_given
