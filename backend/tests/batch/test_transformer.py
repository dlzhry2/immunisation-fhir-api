from collections import OrderedDict

import unittest
from unittest.mock import MagicMock

from batch.errors import DecoratorError, TransformerFieldError, TransformerRowError, \
    TransformerUnhandledError
from batch.transformer import DataRecordTransformer


class TestDatRecordTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = DataRecordTransformer()

        self.decorator0 = MagicMock(name="decorator0")
        self.decorator1 = MagicMock(name="decorator1")
        self.transformer.decorators = [self.decorator0, self.decorator1]

    def test_transform_apply_decorators(self):
        """it should transform the raw imms by applying the decorators"""

        # Given
        # we create two mock decorators. Then we make sure they both contribute to the imms
        def decorator_0(_imms, _record):
            _imms["decorator_0"] = "decorator_0"
            return None

        def decorator_1(_imms, _record):
            _imms["decorator_1"] = "decorator_1"
            return None

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        imms = self.transformer.transform(OrderedDict([]))

        # Then
        decorators_contribution = {
            "decorator_0": "decorator_0",
            "decorator_1": "decorator_1",
        }
        expected_imms = {**self.transformer.raw_imms, **decorators_contribution}
        self.assertEqual(imms, expected_imms)

    def test_accumulate_errors(self):
        """it should keep calling decorators and accumulate errors"""

        def decorator_0(_imms, _record):
            return DecoratorError(errors=[TransformerFieldError("field a and b failed")], decorator_name="decorator_0")

        def decorator_1(_imms, _record):
            return DecoratorError(errors=[TransformerFieldError("field x failed")], decorator_name="decorator_1")

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        with self.assertRaises(TransformerRowError) as e:
            self.transformer.transform(OrderedDict([]))

        # Then
        self.assertEqual(len(e.exception.errors), 2)

    def test_unhandled_error(self):
        """it should raise an error if a decorator throws an error"""

        def decorator_0(_imms, _record):
            raise ValueError("decorator_0")

        def decorator_1(_imms, _record):
            return None

        self.decorator0.side_effect = decorator_0
        self.decorator1.side_effect = decorator_1

        # When
        with self.assertRaises(TransformerUnhandledError) as e:
            self.transformer.transform(OrderedDict([]))

        # Then
        self.assertEqual(e.exception.decorator_name, str(self.decorator0))
        self.decorator1.assert_not_called()
