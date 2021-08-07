import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import NewsEntry, News, InvalidContent, NewsArchive
from tibiapy.enums import NewsCategory, NewsType

FILE_NEWS_LIST = "news/tibiacom_list.txt"
FILE_NEWS_LIST_EMPTY = "news/tibiacom_list_empty.txt"
FILE_NEWS_EMPTY = "news/tibiacom_empty.txt"
FILE_NEWS_ARTICLE = "news/tibiacom_news.txt"
FILE_NEWS_TICKER = "news/tibiacom_news_ticker.txt"


class TestNews(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_news_archive_from_content(self):
        """Testing parsing news"""
        content = self.load_resource(FILE_NEWS_LIST)
        news_archive = NewsArchive.from_content(content)

        self.assertEqual(datetime.date(2019, 3, 25), news_archive.start_date)
        self.assertEqual(datetime.date(2019, 5, 25), news_archive.end_date)
        self.assertEqual(3, len(news_archive.types))
        self.assertEqual(5, len(news_archive.categories))

        news_list = news_archive.entries
        self.assertGreater(len(news_list), 0)
        latest_news = news_list[0]
        self.assertIsInstance(latest_news, NewsEntry)
        self.assertIsInstance(latest_news.id, int)
        self.assertIsInstance(latest_news.category, NewsCategory)
        self.assertIsInstance(latest_news.type, NewsType)
        self.assertIsInstance(latest_news.date, datetime.date)
        self.assertIsNotNone(latest_news.url)
        self.assertEqual(latest_news.url, NewsEntry.get_url(latest_news.id))

    def test_news_archive_from_content_empty(self):
        """Testing parsing a news article that doesn't exist"""
        content = self.load_resource(FILE_NEWS_LIST_EMPTY)
        news_archive = NewsArchive.from_content(content)

        self.assertEqual(datetime.date(2019, 5, 23), news_archive.start_date)
        self.assertEqual(datetime.date(2019, 5, 25), news_archive.end_date)
        self.assertEqual(1, len(news_archive.types))
        self.assertEqual(5, len(news_archive.categories))

        self.assertEqual(0, len(news_archive.entries))

    def test_news_archive_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            NewsArchive.from_content(content)

    def test_news_from_content_empty(self):
        """Testing parsing an empty news article"""
        content = self.load_resource(FILE_NEWS_EMPTY)
        news = News.from_content(content)
        self.assertIsNone(news)

    def test_news_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            News.from_content(content)

    def test_news_from_content_ticker(self):
        """Testing parsing a news ticker"""
        content = self.load_resource(FILE_NEWS_TICKER)
        news = News.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.TECHNICAL_ISSUES)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "News Ticker")
        self.assertIsNone(news.thread_id)

    def test_news_from_content_article(self):
        """Testing parsing an article"""
        content = self.load_resource(FILE_NEWS_ARTICLE)
        news = News.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.DEVELOPMENT)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "Sign Up for the VANGUARD Tournament")
        self.assertEqual(news.thread_id, 4725194)

    # endregion
