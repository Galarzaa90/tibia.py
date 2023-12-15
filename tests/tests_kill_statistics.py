from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.parsers import KillStatisticsParser

FILE_KILL_STATISTICS_FULL = "killStatistics/killStatisticsWithResults.txt"
FILE_KILL_STATISTICS_EMPTY = "killStatistics/killStatisticsEmpty.txt"
FILE_KILL_STATISTICS_NOT_FOUND = "killStatistics/killStatisticsNotFound.txt"


class TestHighscores(TestCommons):

    def test_kill_statistics_from_parser_content(self):
        """Testing parsing kill statistics"""
        content = self.load_resource(FILE_KILL_STATISTICS_FULL)
        kill_statistics = KillStatisticsParser.from_content(content)

        self.assertEqual(kill_statistics.world, "Gladera")
        self.assertSizeEquals(kill_statistics.entries, 1175)
        self.assertIsNotNone(kill_statistics.total)
        self.assertIsNotNone(kill_statistics.url)

        # players shortcurt property
        self.assertEqual(kill_statistics.players, kill_statistics.entries["players"])
        self.assertEqual(kill_statistics.players.last_day_killed, 1)
        self.assertEqual(kill_statistics.players.last_day_killed, kill_statistics.players.last_day_players_killed)
        self.assertEqual(kill_statistics.players.last_week_killed, 2)
        self.assertEqual(kill_statistics.players.last_week_killed, kill_statistics.players.last_week_players_killed)

        # demons
        demons_entry = kill_statistics.entries["demons"]
        self.assertEqual(2299, demons_entry.last_day_killed)
        self.assertEqual(0, demons_entry.last_day_players_killed)
        self.assertEqual(24878, demons_entry.last_week_killed)
        self.assertEqual(3, demons_entry.last_week_players_killed)

    def test_kill_statistics_from_parser_content_empty(self):
        content = self.load_resource(FILE_KILL_STATISTICS_EMPTY)

        kill_statistics = KillStatisticsParser.from_content(content)

        self.assertIsNotNone(kill_statistics)
        self.assertIsEmpty(kill_statistics.entries)

    def test_kill_statistics_from_parser_content_not_found(self):
        """Testing parsing empty kill statistics"""
        content = self.load_resource(FILE_KILL_STATISTICS_NOT_FOUND)
        kill_statistics = KillStatisticsParser.from_content(content)

        self.assertIsNone(kill_statistics)

    def test_kill_statistics_from_parser_content_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            KillStatisticsParser.from_content(content)
