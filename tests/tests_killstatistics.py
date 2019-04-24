from tests.tests_tibiapy import TestTibiaPy
from tibiapy import KillStatistics

FILE_KILL_STATISTICS_FULL = "kill_statistics/tibiacom_full.txt"


class TestHighscores(TestTibiaPy):
    # region Tibia.com Tests
    def testKillStatistics(self):
        content = self._load_resource(FILE_KILL_STATISTICS_FULL)
        kill_statistics = KillStatistics.from_content(content)

        self.assertEqual(kill_statistics.world, "Gladera")
        self.assertEqual(len(kill_statistics.entries), 920)
        self.assertIsNotNone(kill_statistics.total)
    # endregion
