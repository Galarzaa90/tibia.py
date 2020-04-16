import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import KillStatistics, InvalidContent, Tournament

FILE_TOURNAMENT_SIGN_UP_FULL = "tournaments/tournament_information_sign_up.txt"


class TestTournaments(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_tournament_from_content(self):
        """Testing parsing kill statistics"""
        content = self._load_resource(FILE_TOURNAMENT_SIGN_UP_FULL)
        tournament = Tournament.from_content(content)
        self.assertEqual(tournament.title, "TRIUMPH")

    # endregion
