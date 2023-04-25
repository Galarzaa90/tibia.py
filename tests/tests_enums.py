import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy.enums import *


class TestEnums(TestCommons, unittest.TestCase):
    def test_vocation_filter_from_name(self):
        """Testing getting a HighscoresProfession entry from a vocation's name"""
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("elite knight"))
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("knight"))
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("knights"))
        self.assertEqual(HighscoresProfession.ALL, HighscoresProfession.from_name("anything"))
        self.assertIsNone(HighscoresProfession.from_name("anything", all_fallback=False))
