import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, Leaderboard, TournamentEntry, PvpType, RuleSet, ScoreSet, Tournament, \
    TournamentLeaderboard, \
    TournamentPhase

FILE_LEADERBOARD_CURRENT = "leaderboards/tibiacom_current_rotation.txt"


class TestLeaderboards(TestCommons, unittest.TestCase):
    # region Leaderboard Tests
    def test_leaderboard_from_content(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(FILE_LEADERBOARD_CURRENT)
        leaderboard = Leaderboard.from_content(content)

        self.assertIsNotNone(leaderboard)
        self.assertEqual("Antica", leaderboard.world)
        self.assertEqual(2, leaderboard.rotation.rotation_id)
        self.assertEqual(45, leaderboard.results_count)
        self.assertEqual(2, len(leaderboard.available_rotations))
        self.assertEqual(81, len(leaderboard.available_worlds))
        self.assertIsNotNone(leaderboard.url)
        self.assertIsNone(leaderboard.previous_page_url)
        self.assertIsNone(leaderboard.next_page_url)
        self.assertIsNotNone(leaderboard.get_page_url(2))

        first_entry = leaderboard.entries[0]
        self.assertEqual("Daso II", first_entry.name)
        self.assertEqual(1, first_entry.rank)
        self.assertEqual(80, first_entry.drome_level)

    def test_leaderboard_from_content_unrelated_section(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Leaderboard.from_content(content)

    def test_leaderboard_get_url_invalid_page(self):
        with self.assertRaises(ValueError):
            Leaderboard.get_url("Antica", page=0)

    # endregion
