import unittest
from decimal import Decimal

from batch.utils import _is_not_empty, _add_questionnaire_item_to_list, Create, Add, Convert


class TestBatchUtils(unittest.TestCase):
    def setUp(self):
        self.fields_dict = {"key1": "value1", "key2": None, "key3": False, "key4": ""}
        self.fields_dict_non_empty = {"key1": "value1", "key3": False}

    def test_is_not_empty(self):
        for non_empty_value in [False, "Hello", 0, 0.0, {"Key": ""}, ["Hello"]]:
            self.assertTrue(_is_not_empty(non_empty_value))

        for empty_value in [None, "", [], {}, (), [""]]:
            self.assertFalse(_is_not_empty(empty_value))

    def test_add_questionnaire_item_to_list(self):
        items = []

        _add_questionnaire_item_to_list(items, "linkId1", {"valueString": "test1"})
        _add_questionnaire_item_to_list(items, "linkId2", {"valueReference": {"identifier": "identifier1"}})
        _add_questionnaire_item_to_list(items, "linkId3", {"valueBoolean": True})

        expected_items = [
            {"linkId": "linkId1", "answer": [{"valueString": "test1"}]},
            {"linkId": "linkId2", "answer": [{"valueReference": {"identifier": "identifier1"}}]},
            {"linkId": "linkId3", "answer": [{"valueBoolean": True}]},
        ]

        self.assertEqual(items, expected_items)


class TestBatchUtilsConvert(unittest.TestCase):
    def test_convert_date_time(self):
        pass

    def test_convert_date(self):
        pass

    def test_convert_gender_code(self):
        for code, expected in [
            ("1", "male"),
            ("2", "female"),
            ("9", "other"),
            ("0", "unknown"),
            (1, 1),
            ("invalid", "invalid"),
            (None, None),
        ]:
            self.assertEqual(Convert.gender_code(code), expected)

    def test_convert_boolean(self):
        for code, expected in [
            ("true", True),
            ("TRUE", True),
            ("True", True),
            ("false", False),
            ("FALSE", False),
            ("FaLsE", False),
            (1, 1),
            ("invalid", "invalid"),
            (None, None),
        ]:
            self.assertEqual(Convert.boolean(code), expected)

    def test_convert_decimal(self):
        for code, expected in [
            ("1", Decimal("1")),
            ("1.2", Decimal("1.2")),
            ("0", Decimal("0")),
            (["1.2"], ["1.2"]),
            (1, 1),
            ("invalid", "invalid"),
            (None, None),
        ]:
            self.assertEqual(Convert.decimal(code), expected)

    def test_convert_integer(self):
        for code, expected in [
            ("1", 1),
            ("1.2", "1.2"),
            ("0", 0),
            (["1"], ["1"]),
            (1, 1),
            ("invalid", "invalid"),
            (None, None),
        ]:
            self.assertEqual(Convert.integer(code), expected)

    def test_convert_to_lower(self):
        for code, expected in [
            ("1", "1"),
            ("TEST1", "test1"),
            ("test2", "test2"),
            ("teST3", "test3"),
            (["TEST4"], ["TEST4"]),
            (1, 1),
            (None, None),
        ]:
            self.assertEqual(Convert.to_lower(code), expected)


class TestBatchUtilsCreate(unittest.TestCase):
    def test_create_dictionary(self):
        input_dict = {"key1": "value1", "key2": None, "key3": False, "key4": ""}
        expected_output = {"key1": "value1", "key3": False}
        self.assertEqual(Create.dictionary(input_dict), expected_output)

    def test_make_extension_item(self):
        # All values non-empty
        actual = Create.extension_item("testUrl", "testSystem", "ABC", "testDisplay")
        expected = {
            "url": "testUrl",
            "valueCodeableConcept": {"coding": [{"system": "testSystem", "code": "ABC", "display": "testDisplay"}]},
        }
        self.assertEqual(expected, actual)

        # Only display non-empty
        actual = Create.extension_item("testUrl", "testSystem", None, "testDisplay")
        expected = {
            "url": "testUrl",
            "valueCodeableConcept": {"coding": [{"system": "testSystem", "display": "testDisplay"}]},
        }
        self.assertEqual(expected, actual)

        # Only code non-empty
        actual = Create.extension_item("testUrl", "testSystem", "ABC", "")
        expected = {
            "url": "testUrl",
            "valueCodeableConcept": {"coding": [{"system": "testSystem", "code": "ABC"}]},
        }
        self.assertEqual(expected, actual)


class TestBatchUtilsAdd(unittest.TestCase):
    def setUp(self):
        self.test_dict_some_empty = {"key1": "value1", "key2": None, "key3": False, "key4": ""}
        self.test_dict_none_empty = {"key1": "value1", "key3": False}
        self.test_dict_empty = {"key5": "", "key6": None, "key7": []}

    def test_add_item(self):
        test_dict = {}

        # Test non-empty value
        Add.item(test_dict, "key1", "value1")
        self.assertEqual({"key1": "value1"}, test_dict)

        # Test empty value
        Add.item(test_dict, "key2", [])
        self.assertEqual({"key1": "value1"}, test_dict)

        # Test with conversion function
        Add.item(test_dict, "key2", "1", Convert.gender_code)
        self.assertEqual(test_dict, {"key1": "value1", "key2": "male"})

    def test_add_dictionary(self):
        test_dict = {}

        # Test dict with some empty items
        Add.dictionary(test_dict, "test1", self.test_dict_some_empty)
        self.assertEqual(test_dict, {"test1": self.test_dict_none_empty})

        # Test dict with all empty items
        Add.dictionary(test_dict, "test1", self.test_dict_empty)
        self.assertEqual(test_dict, {"test1": self.test_dict_none_empty})

    def test_add_list_of_dictionary(self):
        test_dict = {}

        # Test dict with some empty items
        Add.list_of_dict(test_dict, "test1", self.test_dict_some_empty)
        self.assertEqual(test_dict, {"test1": [self.test_dict_none_empty]})

        # Test dict with all empty items
        Add.list_of_dict(test_dict, "test1", self.test_dict_empty)
        self.assertEqual(test_dict, {"test1": [self.test_dict_none_empty]})

    def test_add_custom_item(self):
        test_dict = {}

        # Test list with some empty items
        Add.custom_item(test_dict, "test1", ["", "test1", None], [{"test1": ["testValue"]}])
        self.assertEqual(test_dict, {"test1": [{"test1": ["testValue"]}]})

        # Test list with all empty items
        Add.custom_item(test_dict, "test2", ["", None], "value2")
        self.assertEqual(test_dict, {"test1": [{"test1": ["testValue"]}]})

    def test_add_snomed(self):
        # Code and display non-empty
        test_dict = {}
        Add.snomed(test_dict, "test1", "ABC", "testDisplay")
        expected = {
            "test1": {"coding": [{"system": "http://snomed.info/sct", "code": "ABC", "display": "testDisplay"}]}
        }
        self.assertEqual(test_dict, expected)

        # Code empty and display non-empty
        test_dict = {}
        Add.snomed(test_dict, "test2", "", "testDisplay")
        expected = {"test2": {"coding": [{"system": "http://snomed.info/sct", "display": "testDisplay"}]}}
        self.assertEqual(test_dict, expected)

        # Code non-empty and display empty
        test_dict = {}
        Add.snomed(test_dict, "test3", "ABC", "")
        expected = {"test3": {"coding": [{"system": "http://snomed.info/sct", "code": "ABC"}]}}
        self.assertEqual(test_dict, expected)

        # Code and display empty
        test_dict = {}
        Add.snomed(test_dict, "test3", "", "")
        self.assertEqual(test_dict, {})

    # def test_make_list_of_dict(self):
    #     self.assertEqual(_make_list_of_dict(self.fields_dict), [self.fields_dict_non_empty])

    # def test_add_dict(self):
    #     test_dict = {}
    #     _add_dict(test_dict, "newField", self.fields_dict)
    #     self.assertEqual({"newField": self.fields_dict_non_empty}, test_dict)

    # def test_add_list_of_dict(self):
    #     test_dict = {}
    #     _add_list_of_dict(test_dict, "newField", self.fields_dict)
    #     self.assertEqual({"newField": [self.fields_dict_non_empty]}, test_dict)

    # # TODO: Add test for _add_custom_item, _add_snomed, all conversion functions
