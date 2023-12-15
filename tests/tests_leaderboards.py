from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.parsers.leaderboard import LeaderboardParser
from tibiapy.urls import get_leaderboards_url

FILE_LEADERBOARD_CURRENT = "leaderboard/leaderboardCurrentRotation.txt"
FILE_LEADERBOARD_DELETED_CHAR = "leaderboard/leaderboardDeletedCharacter.txt"
FILE_LEADERBOARD_NOT_FOUND = "leaderboard/leaderboardNotFound.txt"
FILE_LEADERBOARD_EMPTY = "leaderboard/leaderboardEmpty.txt"


class TestLeaderboards(TestCommons):
    # region Leaderboard Tests
    def test_leaderboard_parser_from_content(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(FILE_LEADERBOARD_CURRENT)
        leaderboard = LeaderboardParser.from_content(content)

        self.assertIsNotNone(leaderboard)
        self.assertEqual("Antica", leaderboard.world)
        self.assertEqual(52, leaderboard.rotation.rotation_id)
        self.assertEqual(475, leaderboard.results_count)
        self.assertEqual(2, len(leaderboard.available_rotations))
        self.assertEqual(90, len(leaderboard.available_worlds))
        self.assertIsNotNone(leaderboard.url)
        self.assertIsNone(leaderboard.previous_page_url)
        self.assertIsNotNone(leaderboard.next_page_url)
        self.assertIsNotNone(leaderboard.get_page_url(2))

        first_entry = leaderboard.entries[0]
        self.assertEqual("Tomoho", first_entry.name)
        self.assertEqual(1, first_entry.rank)
        self.assertEqual(94, first_entry.drome_level)

    def test_leaderboard_parser_from_content_has_deleted_character(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(FILE_LEADERBOARD_DELETED_CHAR)

        leaderboard = LeaderboardParser.from_content(content)

        self.assertIsNotNone(leaderboard)
        self.assertEqual(1, len([e for e in leaderboard.entries if e.name is None]))

    def test_leaderboard_parser_from_content_empty(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(FILE_LEADERBOARD_EMPTY)

        leaderboard = LeaderboardParser.from_content(content)

        self.assertIsNotNone(leaderboard)
        self.assertEqual("Marbera", leaderboard.world)
        self.assertEqual(0, leaderboard.results_count)
        self.assertEqual(0, leaderboard.total_pages)
        self.assertEqual(0, len(leaderboard.entries))

    def test_leaderboard_parser_from_content_world_not_found(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(FILE_LEADERBOARD_NOT_FOUND)

        leaderboard = LeaderboardParser.from_content(content)

        self.assertIsNone(leaderboard)


    def test_leaderboard_parser_from_content_unrelated_section(self):
        """Testing parsing a leaderboard's page"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            LeaderboardParser.from_content(content)

    def test_leaderboard_get_url_invalid_page(self):
        with self.assertRaises(ValueError):
            get_leaderboards_url("Antica", page=0)

    # endregion
