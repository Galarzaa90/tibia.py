from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Highscores, VocationFilter, Category

FILE_HIGHSCORES_FULL = "highscores/tibiacom_full.txt"
FILE_HIGHSCORES_EXPERIENCE = "highscores/tibiacom_experience.txt"
FILE_HIGHSCORES_LOYALTY = "highscores/tibiacom_loyalty.txt"


class TestWorld(TestTibiaPy):

    # region Tibia.com Tests
    def testHighscores(self):
        content = self._load_resource(FILE_HIGHSCORES_FULL)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Estela")
        self.assertEqual(highscores.vocation, VocationFilter.KNIGHTS)
        self.assertEqual(highscores.category, Category.MAGIC_LEVEL)

    def testHighscoresExperience(self):
        content = self._load_resource(FILE_HIGHSCORES_EXPERIENCE)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Gladera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.EXPERIENCE)

    def testHighscoresLoyalty(self):
        content = self._load_resource(FILE_HIGHSCORES_LOYALTY)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Calmera")
        self.assertEqual(highscores.vocation, VocationFilter.PALADINS)
        self.assertEqual(highscores.category, Category.LOYALTY_POINTS)

    # endregion
