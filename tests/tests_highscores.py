from tests.tests_tibiapy import TestCommons
from tibiapy import HighscoresBattlEyeType, HighscoresCategory, HighscoresProfession, InvalidContent, Vocation
from tibiapy.models import Highscores, HighscoresEntry, LoyaltyHighscoresEntry
from tibiapy.parsers import HighscoresParser

FILE_HIGHSCORES_FULL = "highscores/highscores.txt"
FILE_HIGHSCORES_EXPERIENCE = "highscores/highscoresExperience.txt"
FILE_HIGHSCORES_LOYALTY = "highscores/highscoresLoyalty.txt"
FILE_HIGHSCORES_BATTLEYE_PVP_FILTER = "highscores/highscoresBattleEyePvpFilters.txt"
FILE_HIGHSCORES_EMPTY = "highscores/highscoresEmpty.txt"
FILE_HIGHSCORES_NO_RESULTS = "highscores/highscoresNoResults.txt"


class TestHighscores(TestCommons):
    # region Tibia.com Tests
    def test_highscores_parser_from_content(self):
        """Testing parsing Highscores"""
        content = self.load_resource(FILE_HIGHSCORES_FULL)
        highscores = HighscoresParser.from_content(content)

        self.assertEqual("Gladera", highscores.world)
        self.assertEqual(HighscoresProfession.KNIGHTS, highscores.vocation)
        self.assertEqual(HighscoresCategory.MAGIC_LEVEL, highscores.category)
        self.assertEqual(HighscoresBattlEyeType.ANY_WORLD, highscores.battleye_filter)
        self.assertEqual(1688, highscores.results_count)
        self.assertEqual(16, highscores.from_rank)
        self.assertEqual(168, highscores.to_rank)
        self.assertEqual(4, highscores.current_page)
        self.assertEqual(34, highscores.total_pages)
        self.assertIsNotNone(highscores.get_page_url(1))
        self.assertIsNotNone(highscores.url)
        self.assertIsNotNone(highscores.next_page_url)
        self.assertIsNotNone(highscores.previous_page_url)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)
            self.assertEqual("Gladera", entry.world)

    def test_highscores_parser_from_content_experience(self):
        """Testing parsing experience highscores"""
        content = self.load_resource(FILE_HIGHSCORES_EXPERIENCE)
        highscores = HighscoresParser.from_content(content)

        self.assertEqual(highscores.world, "Gladera")
        self.assertEqual(highscores.vocation, HighscoresProfession.PALADINS)
        self.assertEqual(highscores.category, HighscoresCategory.EXPERIENCE)
        self.assertEqual(highscores.results_count, 1000)
        self.assertEqual(highscores.total_pages, 20)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)
            self.assertEqual(entry.world, "Gladera")

    def test_highscores_parser_from_content_loyalty(self):
        """Testing parsing experience loyalty"""
        content = self.load_resource(FILE_HIGHSCORES_LOYALTY)
        highscores = HighscoresParser.from_content(content)

        self.assertEqual("Calmera", highscores.world)
        self.assertEqual(HighscoresProfession.PALADINS, highscores.vocation)
        self.assertEqual(HighscoresCategory.LOYALTY_POINTS, highscores.category)
        self.assertEqual(1000, highscores.results_count)
        self.assertEqual(20, highscores.total_pages)

        for entry in highscores.entries:
            self.assertIsInstance(entry, LoyaltyHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)
            self.assertIsInstance(entry.title, str)

    def test_highscores_parser_from_content_battleye_and_pvp_filters(self):
        """Testing parsing Highscores"""
        content = self.load_resource(FILE_HIGHSCORES_BATTLEYE_PVP_FILTER)
        highscores = HighscoresParser.from_content(content)

        self.assertEqual(None, highscores.world)
        self.assertEqual(HighscoresProfession.ALL, highscores.vocation)
        self.assertEqual(HighscoresCategory.EXPERIENCE, highscores.category)
        self.assertEqual(HighscoresBattlEyeType.INITIALLY_PROTECTED, highscores.battleye_filter)
        self.assertEqual(1000, highscores.results_count)
        self.assertEqual(1, highscores.from_rank)
        self.assertEqual(50, highscores.to_rank)
        self.assertEqual(1, highscores.current_page)
        self.assertEqual(20, highscores.total_pages)
        self.assertEqual(4, len(highscores.pvp_types_filter))
        self.assertIsNotNone(highscores.url)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)

    def test_highscores_parser_from_content_empty(self):
        """Testing parsing highscores when empty (world doesn't exist)"""
        content = self.load_resource(FILE_HIGHSCORES_EMPTY)
        highscores = HighscoresParser.from_content(content)

        self.assertIsNone(highscores)

    def test_highscores_parser_from_content_no_results(self):
        """Testing parsing highscores with no results (first day of a new world)"""
        content = self.load_resource(FILE_HIGHSCORES_NO_RESULTS)
        highscores = HighscoresParser.from_content(content)

        self.assertIsInstance(highscores, Highscores)
        self.assertEqual("Gravitera", highscores.world)
        self.assertEqual(1, highscores.total_pages)
        self.assertEqual(0, len(highscores.entries))
        self.assertEqual(0, highscores.results_count)

    def test_highscores_parser_from_content_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            HighscoresParser.from_content(content)

    # endregion
