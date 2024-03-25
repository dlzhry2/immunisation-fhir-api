import unittest

from utils.batch import BatchFile


class TestBatchProcessing(unittest.TestCase):
    def setUpClass(cls):
        batch_file = BatchFile()
