import unittest
from unittest.mock import create_autospec

from batch.immunization_api import ImmunizationApi
from batch.parser import DataParser
from batch.processor import BatchProcessor, BatchData
from batch.report import ReportGenerator
from batch.transformer import DataRecordTransformer


class TestBatchProcessor(unittest.TestCase):
    def setUp(self):
        self.batch_data = BatchData(
            object_key="an_object_key",
            event_timestamp=1,
            process_timestamp=2,
            environment="a_env",
            source_bucket="a_source_bucket",
            destination_bucket="a_destination_bucket",
            event_id="an_event_id",
            batch_id="a_batch_id",
        )
        self.transformer = create_autospec(DataRecordTransformer)
        self.parser = create_autospec(DataParser)
        self.api = create_autospec(ImmunizationApi)
        self.report_gen = create_autospec(ReportGenerator)
        self.processor = BatchProcessor(
            batch_data=self.batch_data,
            row_transformer=self.transformer,
            parser=self.parser,
            api=self.api,
            report_generator=self.report_gen,
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
