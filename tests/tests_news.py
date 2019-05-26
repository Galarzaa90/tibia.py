import datetime

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import ListedNews, News, InvalidContent
from tibiapy.enums import NewsCategory, NewsType

FILE_NEWS_LIST = "news/tibiacom_list.txt"
FILE_NEWS_LIST_EMPTY = "news/tibiacom_list_empty.txt"
FILE_NEWS_EMPTY = "news/tibiacom_empty.txt"
FILE_NEWS_ARTICLE = "news/tibiacom_news.txt"
FILE_NEWS_TICKER = "news/tibiacom_news_ticker.txt"


class TestNews(TestTibiaPy):
    # region Tibia.com Tests
    def testNewsList(self):
        content = self._load_resource(FILE_NEWS_LIST)
        news_list = ListedNews.list_from_content(content)
        self.assertGreater(len(news_list), 0)
        latest_news = news_list[0]

        self.assertIsInstance(latest_news, ListedNews)
        self.assertIsInstance(latest_news.id, int)
        self.assertIsInstance(latest_news.category, NewsCategory)
        self.assertIsInstance(latest_news.type, NewsType)
        self.assertIsInstance(latest_news.date, datetime.date)
        self.assertIsNotNone(latest_news.url)
        self.assertEqual(latest_news.url, ListedNews.get_url(latest_news.id))

    def testNewsListEmpty(self):
        content = self._load_resource(FILE_NEWS_LIST_EMPTY)
        news_list = ListedNews.list_from_content(content)
        self.assertEqual(len(news_list), 0)

    def testNewsListUnrelated(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            ListedNews.list_from_content(content)

    def testNewsEmpty(self):
        content = self._load_resource(FILE_NEWS_EMPTY)
        news = News.from_content(content)
        self.assertIsNone(news)

    def testNewsUnrelated(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            News.from_content(content)

    def testNewsTicker(self):
        content = self._load_resource(FILE_NEWS_TICKER)
        news = News.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.TECHNICAL_ISSUES)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "News Ticker")
        self.assertIsNone(news.thread_id)

    def testNewsArticle(self):
        content = self._load_resource(FILE_NEWS_ARTICLE)
        news = News.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.DEVELOPMENT)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "Sign Up for the VANGUARD Tournament")
        self.assertEqual(news.thread_id, 4725194)

    # endregion
