import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.models.news import NewsEntry, NewsArchive, News
from tibiapy.parsers.news import NewsArchiveParser, NewsParser

FILE_NEWS_ARCHIVE_INITIAL = "news/news_archive_initial.txt"
FILE_NEWS_ARCHIVE_RESULTS = "news/news_archive_results.txt"
FILE_NEWS_ARCHIVE_EMPTY = "news/news_archive_empty.txt"
FILE_NEWS_ARCHIVE_ERROR = "news/news_archive_error.txt"
FILE_NEWS_NOT_FOUND = "news/news_not_found.txt"
FILE_NEWS_ARTICLE = "news/news_article.txt"
FILE_NEWS_TICKER = "news/news_ticker.txt"


class TestNews(TestCommons, unittest.TestCase):
    def test_news_archive_parser_from_content_initial(self):
        """Test parsing the news archive initial page."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_INITIAL)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertIsInstance(news_archive, NewsArchive)
        self.assertEqual(datetime.date(2023, 3, 16), news_archive.start_date)
        self.assertEqual(datetime.date(2023, 4, 15), news_archive.end_date)
        self.assertEqual(3, len(news_archive.types))
        self.assertEqual(5, len(news_archive.categories))

    def test_news_archive_parser_from_content_with_results(self):
        """Testing parsing the news archive with results."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_RESULTS)

        news_archive = NewsArchiveParser.from_content(content)

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

    def test_news_archive_parser_from_content_empty(self):
        """Testing parsing a news article that doesn't exist"""
        content = self.load_resource(FILE_NEWS_ARCHIVE_EMPTY)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertEqual(datetime.date(2023, 4, 13), news_archive.start_date)
        self.assertEqual(datetime.date(2023, 4, 15), news_archive.end_date)
        self.assertEqual(1, len(news_archive.types))
        self.assertEqual(5, len(news_archive.categories))
        self.assertEqual(0, len(news_archive.entries))

    def test_news_archive_parser_from_content_error(self):
        """Testing parsing the news archive resulting in an error message."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_ERROR)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertIsInstance(news_archive, NewsArchive)
        self.assertEqual(datetime.date(2019, 3, 25), news_archive.start_date)
        self.assertEqual(datetime.date(2018, 5, 25), news_archive.end_date)
        self.assertEqual(3, len(news_archive.types))
        self.assertEqual(5, len(news_archive.categories))
        self.assertEqual(0, len(news_archive.entries))

    def test_news_archive_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            NewsArchiveParser.from_content(content)

    def test_news_parser_from_content_empty(self):
        """Testing parsing an empty news article"""
        content = self.load_resource(FILE_NEWS_NOT_FOUND)
        news = NewsParser.from_content(content)
        self.assertIsNone(news)

    def test_news_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            NewsParser.from_content(content)

    def test_news_parser_from_content_ticker(self):
        """Testing parsing a news ticker"""
        content = self.load_resource(FILE_NEWS_TICKER)
        news = NewsParser.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.TECHNICAL_ISSUES)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "News Ticker")
        self.assertIsNone(news.thread_id)

    def test_news_parser_from_content_article(self):
        """Testing parsing an article"""
        content = self.load_resource(FILE_NEWS_ARTICLE)
        news = NewsParser.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.DEVELOPMENT)
        self.assertIsInstance(news.date, datetime.date)
        self.assertEqual(news.title, "Sign Up for the VANGUARD Tournament")
        self.assertEqual(news.thread_id, 4725194)


