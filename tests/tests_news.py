import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import ListedNews, News, InvalidContent
from tibiapy.enums import NewsCategory, NewsType

FILE_NEWS_LIST = "news/tibiacom_list.txt"
FILE_NEWS_LIST_EMPTY = "news/tibiacom_list_empty.txt"
FILE_NEWS_EMPTY = "news/tibiacom_empty.txt"
FILE_NEWS_ARTICLE = "news/tibiacom_news.txt"
FILE_NEWS_TICKER = "news/tibiacom_news_ticker.txt"


class TestNews(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_listed_news_from_content(self):
        """Testing parsing news"""
        content = self.load_resource(FILE_NEWS_LIST)
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

    def test_listed_news_from_content_empty(self):
        """Testing parsing a news article that doesn't exist"""
        content = self.load_resource(FILE_NEWS_LIST_EMPTY)
        news_list = ListedNews.list_from_content(content)
        self.assertEqual(len(news_list), 0)

    def test_listed_news_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            ListedNews.list_from_content(content)

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
