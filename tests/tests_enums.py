import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy.enums import *


class TestEnums(TestCommons, unittest.TestCase):
    def test_vocation_filter_from_name(self):
        """Testing getting a VocationFilter entry from a vocation's name"""
        self.assertEqual(VocationFilter.KNIGHTS, VocationFilter.from_name("elite knight"))
        self.assertEqual(VocationFilter.KNIGHTS, VocationFilter.from_name("knight"))
        self.assertEqual(VocationFilter.KNIGHTS, VocationFilter.from_name("knights"))
        self.assertEqual(VocationFilter.ALL, VocationFilter.from_name("anything"))
        self.assertIsNone(VocationFilter.from_name("anything", all_fallback=False))
