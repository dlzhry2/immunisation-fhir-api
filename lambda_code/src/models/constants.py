import re
from datetime import datetime


class Constants:
    genders = {"0", "1", "2", "9"}
    action_flags = {"completed", "entered-in-error"}
    vaccination_not_given_flag: str = "not-done"
    vaccination_given_flag: str = "empty"

    @staticmethod
    def convert_iso8601_to_datetime(iso_datetime_str):
        try:
            time_str = "T00:00:00+00:00"
            # Check if time information is present
            if "T" in iso_datetime_str:
                # Check if timezone information is present
                if "+" in iso_datetime_str:
                    # Add the colon (:00) in the timezone offset
                    timestamp_str_with_colon = iso_datetime_str + ":00"
                    dt_obj = datetime.strptime(
                        timestamp_str_with_colon, "%Y-%m-%dT%H:%M:%S%z"
                    )
                else:
                    dt_obj = datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%S")
            else:
                # Add the the timezone offset
                timestamp_str_with_colon = iso_datetime_str + time_str
                dt_obj = datetime.strptime(
                    timestamp_str_with_colon, "%Y-%m-%dT%H:%M:%S%z"
                )

            return dt_obj
        except ValueError:
            raise ValueError("Invalid datetime format. Use YYYY-MM-DDThh:mm:ss+zz.")

    @staticmethod
    def convert_to_date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    @staticmethod
    def is_urn_resource(s):
        # Check if the lowercase version of the string starts with "urn"
        return s.lower().startswith("urn")

    @staticmethod
    def if_vaccine_not_give(not_given_flag):
        if not not_given_flag or not_given_flag == Constants.vaccination_given_flag:
            return False
        else:
            if not_given_flag == Constants.vaccination_not_given_flag:
                return True

    @staticmethod
    def has_max_decimal_places(input_string, max_places=4):
        # Define a regular expression pattern for matching up to four decimal places
        pattern = r"^\d+(\.\d{1,4})?$"

        # Use re.match to check if the input matches the pattern
        return bool(re.match(pattern, input_string))
