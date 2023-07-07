import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy.enums import *
from tibiapy.models import AuctionFilters


class TestEnums(TestCommons, unittest.TestCase):

    def test_numeric_enum_serialization(self):
        filters = AuctionFilters(battleye=AuctionBattlEyeFilter.INITIALLY_PROTECTED)

        json_filters = filters.model_dump_json()

        self.assertIn('"battleye":"INITIALLY_PROTECTED"', json_filters)

    def test_numeric_enum_deserialization(self):
        json_filters = '{"battleye":"INITIALLY_PROTECTED"}'

        filters = AuctionFilters.model_validate_json(json_filters)

        self.assertEqual(filters.battleye, AuctionBattlEyeFilter.INITIALLY_PROTECTED)

    def test_vocation_filter_from_name(self):
        """Testing getting a HighscoresProfession entry from a vocation's name"""
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("elite knight"))
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("knight"))
        self.assertEqual(HighscoresProfession.KNIGHTS, HighscoresProfession.from_name("knights"))
        self.assertEqual(HighscoresProfession.ALL, HighscoresProfession.from_name("anything"))
        self.assertIsNone(HighscoresProfession.from_name("anything", all_fallback=False))
