"""Tests for utils_for_filenameprocessor functions"""

from unittest import TestCase
from moto import mock_s3

from utils_for_filenameprocessor import get_csv_content_dict_reader, identify_supplier
from tests.utils_for_tests.utils_for_filenameprocessor_tests import setup_s3_bucket_and_file


@mock_s3
class TestUtilsForFilenameprocessor(TestCase):
    """Tests for utils_for_filenameprocessor functions"""

    def test_get_csv_content_dict_reader(self):
        """Test that get_csv_content_dict_reader can download and correctly read the data file"""
        bucket_name = "test_bucket"
        file_key = "test_file_key"
        file_content = "HEADER1|HEADER2\nvalue1|value2"
        setup_s3_bucket_and_file(bucket_name, file_key, file_content)

        csv_content_dict_reader = get_csv_content_dict_reader(bucket_name, file_key)

        for row in csv_content_dict_reader:
            self.assertEqual(row.get("HEADER1"), "value1")
            self.assertEqual(row.get("HEADER2"), "value2")

    def test_identify_supplier(self):
        """Test that identify_supplier correctly identifies supplier using ods_to_supplier_mappings"""
        # Each test case tuple has the structure (ods_code, expected_result)
        test_cases = (
            ("YGM41", "EMIS"),
            ("8J1100001", "PINNACLE"),
            ("8HK48", "SONAR"),
            ("YGA", "TPP"),
            ("0DE", "AGEM-NIVS"),
            ("0DF", "NIMS"),
            ("8HA94", "EVA"),
            ("X26", "RAVS"),
            ("YGMYH", "MEDICAL_DIRECTOR"),
            ("W00", "WELSH_DA_1"),
            ("W000", "WELSH_DA_2"),
            ("ZT001", "NORTHERN_IRELAND_DA"),
            ("YA7", "SCOTLAND_DA"),
            ("N2N9I", "COVID19_VACCINE_RESOLUTION_SERVICEDESK"),
            ("YGJ", "EMIS"),
            ("DPSREDUCED", "DPSREDUCED"),
            ("DPSFULL", "DPSFULL"),
            ("NOT_A_VALID_ODS_CODE", ""),  # Should default to empty string if ods code isn't in the mappings
        )

        for ods_code, expected_result in test_cases:
            with self.subTest(f"SubTest for ODS code: {ods_code}"):
                self.assertEqual(identify_supplier(ods_code), expected_result)
