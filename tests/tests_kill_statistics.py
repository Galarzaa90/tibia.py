import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import KillStatistics, InvalidContent

FILE_KILL_STATISTICS_FULL = "kill_statistics/tibiacom_full.txt"
FILE_KILL_STATISTICS_EMPTY = "kill_statistics/tibiacom_empty.txt"


class TestHighscores(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_kill_statistics_from_content(self):
        """Testing parsing kill statistics"""
        content = self._load_resource(FILE_KILL_STATISTICS_FULL)
        kill_statistics = KillStatistics.from_content(content)

        self.assertEqual(kill_statistics.world, "Gladera")
        self.assertEqual(len(kill_statistics.entries), 920)
        self.assertIsNotNone(kill_statistics.total)
        self.assertIsNotNone(kill_statistics.url)

        # players shortcurt property
        self.assertEqual(kill_statistics.players, kill_statistics.entries["players"])
        self.assertEqual(kill_statistics.players.last_day_killed, 2)
        self.assertEqual(kill_statistics.players.last_day_killed, kill_statistics.players.last_day_players_killed)
        self.assertEqual(kill_statistics.players.last_week_killed, 7)
        self.assertEqual(kill_statistics.players.last_week_killed, kill_statistics.players.last_week_players_killed)

        # demons
        demons_entry = kill_statistics.entries["demons"]
        self.assertEqual(2071, demons_entry.last_day_killed)
        self.assertEqual(1, demons_entry.last_day_players_killed)
        self.assertEqual(18484, demons_entry.last_week_killed)
        self.assertEqual(8, demons_entry.last_week_players_killed)

    def test_kill_statistics_from_content_empty(self):
        """Testing parsing empty kill statistics"""
        content = self._load_resource(FILE_KILL_STATISTICS_EMPTY)
        kill_statistics = KillStatistics.from_content(content)

        self.assertIsNone(kill_statistics)

    def test_kill_statistics_from_content_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            KillStatistics.from_content(content)

    # endregion
