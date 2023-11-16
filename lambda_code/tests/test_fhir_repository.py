import os
import sys
import unittest

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../src")

from fhir_repository import ImmunisationRepository


class TestImmunisationRepository(unittest.TestCase):
    def setUp(self):
        self.repository = ImmunisationRepository(table_name="a-table")

    def test_get_immunisation_by_id(self):
        """it should find an Immunization by id"""
        pass
