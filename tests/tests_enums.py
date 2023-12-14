import tibiapy.enums
from tests.tests_tibiapy import TestCommons
from tibiapy.models import AuctionFilters


class TestEnums(TestCommons):

    def test_numeric_enum_serialization(self):
        filters = AuctionFilters(battleye=tibiapy.enums.AuctionBattlEyeFilter.INITIALLY_PROTECTED)

        json_filters = filters.model_dump_json()

        self.assertIn('"battleye":"INITIALLY_PROTECTED"', json_filters)

    def test_numeric_enum_deserialization(self):
        json_filters = '{"battleye":"INITIALLY_PROTECTED"}'

        filters = AuctionFilters.model_validate_json(json_filters)

        self.assertEqual(filters.battleye, tibiapy.enums.AuctionBattlEyeFilter.INITIALLY_PROTECTED)

    def test_vocation_filter_from_name(self):
        """Testing getting a HighscoresProfession entry from a vocation's name"""
        self.assertEqual(tibiapy.enums.HighscoresProfession.KNIGHTS,
                         tibiapy.enums.HighscoresProfession.from_name("elite knight"))
        self.assertEqual(tibiapy.enums.HighscoresProfession.KNIGHTS,
                         tibiapy.enums.HighscoresProfession.from_name("knight"))
        self.assertEqual(tibiapy.enums.HighscoresProfession.KNIGHTS,
                         tibiapy.enums.HighscoresProfession.from_name("knights"))
        self.assertEqual(tibiapy.enums.HighscoresProfession.ALL,
                         tibiapy.enums.HighscoresProfession.from_name("anything"))
        self.assertIsNone(tibiapy.enums.HighscoresProfession.from_name("anything", all_fallback=False))
