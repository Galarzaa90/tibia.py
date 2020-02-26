import unittest

import tests.tests_character
from tests.tests_tibiapy import TestCommons
from tibiapy import Category, ExpHighscoresEntry, Highscores, HighscoresEntry, InvalidContent, LoyaltyHighscoresEntry, \
    Vocation, VocationFilter

FILE_HIGHSCORES_FULL = "highscores/tibiacom_full.txt"
FILE_HIGHSCORES_EXPERIENCE = "highscores/tibiacom_experience.txt"
FILE_HIGHSCORES_LOYALTY = "highscores/tibiacom_loyalty.txt"
FILE_HIGHSCORES_EMPTY = "highscores/tibiacom_empty.txt"
FILE_HIGHSCORES_NO_RESULTS = "highscores/tibiacom_no_results.txt"

FILE_HIGHSCORES_TIBIADATA_FULL = "highscores/tibiadata_full.json"
FILE_HIGHSCORES_TIBIADATA_EXPERIENCE = "highscores/tibiadata_experience.json"
FILE_HIGHSCORES_TIBIADATA_LOYALTY = "highscores/tibiadata_loyalty.json"
FILE_HIGHSCORES_TIBIADATA_EMPTY = "highscores/tibiadata_empty.json"


class TestHighscores(unittest.TestCase, TestCommons):
    # region Tibia.com Tests
    def test_highscores_from_content(self):
        """Testing parsing Highscores"""
        content = self._load_resource(FILE_HIGHSCORES_FULL)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Estela")
        self.assertEqual(highscores.vocation, VocationFilter.KNIGHTS)
        self.assertEqual(highscores.category, Category.MAGIC_LEVEL)
        self.assertEqual(highscores.results_count, 300)
        self.assertEqual(highscores.from_rank, 76)
        self.assertEqual(highscores.to_rank, 100)
        self.assertEqual(highscores.page, 4)
        self.assertEqual(highscores.total_pages, 12)
        self.assertIsNotNone(highscores.url)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)

    def test_highscores_from_content_highscores(self):
        """Testing parsing experience highscores"""
        content = self._load_resource(FILE_HIGHSCORES_EXPERIENCE)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Gladera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.EXPERIENCE)
        self.assertEqual(highscores.results_count, 300)
        self.assertEqual(highscores.total_pages, 12)

        for entry in highscores.entries:
            self.assertIsInstance(entry, ExpHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)

    def test_highscores_from_content_loyalty(self):
        """Testing parsing experience loyalty"""
        content = self._load_resource(FILE_HIGHSCORES_LOYALTY)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Calmera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.LOYALTY_POINTS)
        self.assertEqual(highscores.results_count, 65)
        self.assertEqual(highscores.total_pages, 3)

        for entry in highscores.entries:
            self.assertIsInstance(entry, LoyaltyHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.title, str)

    def test_highscores_from_content_empty(self):
        """Testing parsing highscores when empty (world doesn't exist)"""
        content = self._load_resource(FILE_HIGHSCORES_EMPTY)
        highscores = Highscores.from_content(content)

        self.assertIsNone(highscores)

    def test_highscores_from_content_no_results(self):
        """Testing parsing highscores with no results (first day of a new world)"""
        content = self._load_resource(FILE_HIGHSCORES_NO_RESULTS)
        highscores = Highscores.from_content(content)

        self.assertIsInstance(highscores, Highscores)
        self.assertEqual(highscores.world, "Unica")
        self.assertEqual(highscores.category, Category.EXPERIENCE)
        self.assertEqual(highscores.vocation, VocationFilter.ALL)
        self.assertEqual(highscores.total_pages, 0)
        self.assertEqual(len(highscores.entries), 0)

    def test_highscores_from_content_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Highscores.from_content(content)

    # endregion

    # region TibiaData.com Tests
    def test_highscores_from_tibiadata(self):
        """Testing parsing highscores from TibiaData"""
        content = self._load_resource(FILE_HIGHSCORES_TIBIADATA_FULL)
        highscores = Highscores.from_tibiadata(content)

        self.assertEqual(highscores.world, "Antica")
        self.assertEqual(highscores.vocation, VocationFilter.ALL)
        self.assertEqual(highscores.category, Category.AXE_FIGHTING)
        self.assertEqual(highscores.results_count, 300)

        self.assertEqual(highscores.url_tibiadata,
                         Highscores.get_url_tibiadata(highscores.world, highscores.category, highscores.vocation))

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)

    def test_highscores_from_tibiadata_experience(self):
        """Testing parsing experience highscores"""
        content = self._load_resource(FILE_HIGHSCORES_TIBIADATA_EXPERIENCE)
        highscores = Highscores.from_tibiadata(content)

        self.assertEqual(highscores.world, "Luminera")
        self.assertEqual(highscores.vocation, VocationFilter.ALL)
        self.assertEqual(highscores.category, Category.EXPERIENCE)
        self.assertEqual(highscores.results_count, 300)

        for entry in highscores.entries:
            self.assertIsInstance(entry, ExpHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)

    def test_highscores_from_tibiadata_loyalty(self):
        """Testing parsing loyalty highscores"""
        content = self._load_resource(FILE_HIGHSCORES_TIBIADATA_LOYALTY)
        highscores = Highscores.from_tibiadata(content)

        self.assertEqual(highscores.world, "Zunera")
        self.assertEqual(highscores.vocation, VocationFilter.ALL)
        self.assertEqual(highscores.category, Category.LOYALTY_POINTS)
        self.assertEqual(highscores.results_count, 57)

        for entry in highscores.entries:
            self.assertIsInstance(entry, LoyaltyHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.title, str)

    def test_highscores_from_tibiadata_empty(self):
        """Testing parsing empty highscores"""
        content = self._load_resource(FILE_HIGHSCORES_TIBIADATA_EMPTY)
        highscores = Highscores.from_tibiadata(content)

        self.assertIsNone(highscores)

    def test_highscores_from_tibiadata_unrelated_section(self):
        """Testing parsing an unrelated section"""
        with self.assertRaises(InvalidContent):
            Highscores.from_tibiadata(self._load_resource(tests.tests_character.FILE_CHARACTER_TIBIADATA))

    # endregion
