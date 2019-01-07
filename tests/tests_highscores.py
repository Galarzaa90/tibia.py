from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Category, ExpHighscoresEntry, Highscores, HighscoresEntry, LoyaltyHighscoresEntry, Vocation, \
    VocationFilter

FILE_HIGHSCORES_FULL = "highscores/tibiacom_full.txt"
FILE_HIGHSCORES_EXPERIENCE = "highscores/tibiacom_experience.txt"
FILE_HIGHSCORES_LOYALTY = "highscores/tibiacom_loyalty.txt"
FILE_HIGHSCORES_EMPTY = "highscores/tibiacom_empty.txt"


class TestHighscores(TestTibiaPy):
    # region Tibia.com Tests
    def testHighscores(self):
        content = self._load_resource(FILE_HIGHSCORES_FULL)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Estela")
        self.assertEqual(highscores.vocation, VocationFilter.KNIGHTS)
        self.assertEqual(highscores.category, Category.MAGIC_LEVEL)
        self.assertEqual(highscores.results_count, 300)

        for entry in highscores.entries:
            self.assertIsInstance(entry, HighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)

    def testHighscoresExperience(self):
        content = self._load_resource(FILE_HIGHSCORES_EXPERIENCE)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Gladera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.EXPERIENCE)
        self.assertEqual(highscores.results_count, 300)

        for entry in highscores.entries:
            self.assertIsInstance(entry, ExpHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.level, int)

    def testHighscoresLoyalty(self):
        content = self._load_resource(FILE_HIGHSCORES_LOYALTY)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Calmera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.LOYALTY_POINTS)
        self.assertEqual(highscores.results_count, 65)

        for entry in highscores.entries:
            self.assertIsInstance(entry, LoyaltyHighscoresEntry)
            self.assertIsInstance(entry.name, str)
            self.assertIsInstance(entry.vocation, Vocation)
            self.assertIsInstance(entry.rank, int)
            self.assertIsInstance(entry.value, int)
            self.assertIsInstance(entry.title, str)

    def testHighscoresEmpty(self):
        content = self._load_resource(FILE_HIGHSCORES_EMPTY)
        highscores = Highscores.from_content(content)

        self.assertIsNone(highscores)

    # endregion
