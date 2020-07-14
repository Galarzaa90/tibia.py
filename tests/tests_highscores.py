import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import Category, Highscores, HighscoresEntry, InvalidContent, LoyaltyHighscoresEntry, \
    Vocation, VocationFilter

FILE_HIGHSCORES_FULL = "highscores/tibiacom_full.txt"
FILE_HIGHSCORES_EXPERIENCE = "highscores/tibiacom_experience.txt"
FILE_HIGHSCORES_LOYALTY = "highscores/tibiacom_loyalty.txt"
FILE_HIGHSCORES_EMPTY = "highscores/tibiacom_empty.txt"
FILE_HIGHSCORES_NO_RESULTS = "highscores/tibiacom_no_results.txt"


class TestHighscores(unittest.TestCase, TestCommons):
    # region Tibia.com Tests
    def test_highscores_from_content(self):
        """Testing parsing Highscores"""
        content = self.load_resource(FILE_HIGHSCORES_FULL)
        highscores = Highscores.from_content(content)

        self.assertEqual("Estela", highscores.world)
        self.assertEqual(VocationFilter.KNIGHTS, highscores.vocation)
        self.assertEqual(Category.MAGIC_LEVEL, highscores.category)
        self.assertEqual(1932, highscores.results_count)
        self.assertEqual(31, highscores.from_rank)
        self.assertEqual(31, highscores.to_rank)
        self.assertEqual(4, highscores.page)
        self.assertEqual(39, highscores.total_pages)
        self.assertIsNotNone(highscores.url)
        self.assertEqual(datetime.timedelta(minutes=2), highscores.last_updated)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertEqual("Estela", entry.world)

    def test_highscores_from_content_highscores(self):
        """Testing parsing experience highscores"""
        content = self.load_resource(FILE_HIGHSCORES_EXPERIENCE)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Gladera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.EXPERIENCE)
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

    def test_highscores_from_content_loyalty(self):
        """Testing parsing experience loyalty"""
        content = self.load_resource(FILE_HIGHSCORES_LOYALTY)
        highscores = Highscores.from_content(content)

        self.assertEqual("Calmera", highscores.world)
        self.assertEqual(VocationFilter.PALADINS, highscores.vocation)
        self.assertEqual(Category.LOYALTY_POINTS, highscores.category)
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

    def _test_highscores_from_content_empty(self):
        """Testing parsing highscores when empty (world doesn't exist)"""
        content = self.load_resource(FILE_HIGHSCORES_EMPTY)
        highscores = Highscores.from_content(content)

        self.assertIsNone(highscores)

    def _test_highscores_from_content_no_results(self):
        """Testing parsing highscores with no results (first day of a new world)"""
        content = self.load_resource(FILE_HIGHSCORES_NO_RESULTS)
        highscores = Highscores.from_content(content)

        self.assertIsInstance(highscores, Highscores)
        self.assertEqual(highscores.world, "Unica")
        self.assertEqual(highscores.category, Category.EXPERIENCE)
        self.assertEqual(highscores.vocation, VocationFilter.ALL)
        self.assertEqual(highscores.total_pages, 0)
        self.assertEqual(len(highscores.entries), 0)

    def test_highscores_from_content_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Highscores.from_content(content)

    # endregion
