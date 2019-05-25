from tests.tests_tibiapy import TestTibiaPy
from tibiapy import ListedNews

FILE_NEWS_LIST = "news/tibiacom_list.txt"


class TestHighscores(TestTibiaPy):
    # region Tibia.com Tests
    def testKillStatistics(self):
        content = self._load_resource(FILE_NEWS_LIST)
        news = ListedNews.from_content(content)

    # endregion
