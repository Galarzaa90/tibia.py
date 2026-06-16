import tibiapy.enums
from tests.tests_tibiapy import TestCommons
from tibiapy.models import AuctionFilters
from tibiapy.utils import try_enum


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

    def test_vocation_includes_monk(self):
        """Monk vocations must resolve, otherwise bazaar pages containing a Monk fail to parse."""
        self.assertEqual(tibiapy.enums.Vocation.MONK, tibiapy.enums.Vocation("Monk"))
        self.assertEqual(tibiapy.enums.Vocation.EXALTED_MONK, tibiapy.enums.Vocation("Exalted Monk"))
        self.assertEqual(tibiapy.enums.Vocation.MONK, tibiapy.enums.Vocation.EXALTED_MONK.base)
        # The bazaar parser resolves vocations through try_enum; "Monk" previously returned None.
        self.assertEqual(tibiapy.enums.Vocation.MONK, try_enum(tibiapy.enums.Vocation, "Monk"))
        self.assertEqual(tibiapy.enums.Vocation.EXALTED_MONK,
                         try_enum(tibiapy.enums.Vocation, "Exalted Monk"))
