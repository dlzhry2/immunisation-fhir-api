import unittest
from unittest.mock import create_autospec

from batch.immunization_api import ImmunizationApi
from batch.parser import DataParser
from batch.processor import BatchProcessor
from batch.transformer import DataRecordTransformer


class TestBatchProcessor(unittest.TestCase):
    def setUp(self):
        self.transformer = create_autospec(DataRecordTransformer)
        self.parser = create_autospec(DataParser)
        self.api = create_autospec(ImmunizationApi)
        self.processor = BatchProcessor(
            row_transformer=self.transformer,
            parser=self.parser,
            api=self.api
        )

    def test_create_dict_record(self):
        """it should create a dictionary record from the headers and row"""
        self.parser.parse_rows.return_value = iter([["H0", "H1"], ["v0", "v1"]])

        self.processor.process()

        # The headers should be converted to the lower case value
        self.transformer.transform.assert_called_once_with({"h0": "v0", "h1": "v1"})

    def test_send_transformed_record(self):
        """it should create a dictionary record from the headers and row"""
        self.parser.parse_rows.return_value = iter([["H0", "H1"], ["v0", "v1"]])
        imms = {"key": "value"}
        self.transformer.transform.return_value = imms

        self.processor.process()

        self.api.create_immunization.assert_called_once_with(imms)

    def test_continue_on_transform_error(self):
        """it should continue processing if a transform error is raised"""
        self.parser.parse_rows.return_value = iter([["H0", "H1"], ["v0", "v1"]])
        self.transformer.transform.side_effect = Exception("Boom")

        self.processor.process()

        self.api.create_immunization.assert_not_called()
