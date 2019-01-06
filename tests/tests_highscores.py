from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Highscores, VocationFilter, Category

FILE_HIGHSCORES_FULL = "highscores/tibiacom_full.txt"


class TestWorld(TestTibiaPy):

    # region Tibia.com Tests
    def testWorld(self):
        content = self._load_resource(FILE_HIGHSCORES_FULL)
        highscores = Highscores.from_content(content)

        self.assertEqual(highscores.world, "Estela")
        self.assertEqual(highscores.vocation, VocationFilter.KNIGHTS)
        self.assertEqual(highscores.category, Category.MAGIC_LEVEL)

    # endregion
