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

        first_entry = leaderboard.entries[0]
        self.assertEqual("Daso II", first_entry.name)
        self.assertEqual(1, first_entry.rank)
        self.assertEqual(80, first_entry.drome_level)
    # endregion
