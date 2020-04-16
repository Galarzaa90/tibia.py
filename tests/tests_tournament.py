import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import PvpType, RuleSet, Tournament

FILE_TOURNAMENT_SIGN_UP_FULL = "tournaments/tournament_information_sign_up.txt"


class TestTournaments(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_tournament_from_content(self):
        """Testing parsing kill statistics"""
        content = self._load_resource(FILE_TOURNAMENT_SIGN_UP_FULL)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "TRIUMPH")
        self.assertEqual(6, len(tournament.worlds))
        self.assertEqual("sign up", tournament.phase)
        self.assertIsInstance(tournament.start_date, datetime.datetime)
        self.assertIsInstance(tournament.end_date, datetime.datetime)
        self.assertIsInstance(tournament.rule_set, RuleSet)

        # Rule Set
        rule_set = tournament.rule_set
        self.assertEqual(PvpType.OPEN_PVP, rule_set.pvp_type)
        self.assertIsInstance(rule_set.daily_tournament_playtime, datetime.timedelta)
        self.assertEqual(datetime.timedelta(hours=4), rule_set.daily_tournament_playtime)
        self.assertEqual(datetime.timedelta(hours=14), rule_set.daily_tournament_playtime)
        self.assertEqual(4, rule_set.house_auction_durations)
        self.assertEqual(2.0, rule_set.death_penalty_modifier)
        self.assertEqual(2.0, rule_set.loot_probability)
        self.assertEqual(2.0, rule_set.xp_multiplier)
        self.assertEqual(10.0, rule_set.skill_multiplier)
        self.assertEqual(10, rule_set.rent_percentage)
        self.assertTrue(rule_set.playtime_reduced_only_in_combat)

        # Score Set

    # endregion
