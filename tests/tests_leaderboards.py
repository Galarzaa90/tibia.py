import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, Leaderboard, ListedTournament, PvpType, RuleSet, ScoreSet, Tournament, \
    TournamentLeaderboard, \
    TournamentPhase

FILE_LEADERBOARD_CURRENT = "leaderboards/tibiacom_current_rotation.txt"


class TestLeaderboards(TestCommons, unittest.TestCase):
    # region Leaderboard Tests
    def test_leaderboard_from_content(self):
        """Testing parsing a tournament's info page"""
        content = self.load_resource(FILE_LEADERBOARD_CURRENT)
        leaderboard = Leaderboard.from_content(content)
        pass
    # endregion
