import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.enums import NewsCategory, NewsType
from tibiapy.models import NewsEntry, NewsArchive, News
from tibiapy.parsers import NewsArchiveParser, NewsParser
from tibiapy.urls import get_news_url

FILE_NEWS_ARCHIVE_INITIAL = "newsArchive/newsArchiveInitial.txt"
FILE_NEWS_ARCHIVE_RESULTS_FILTERED = "newsArchive/newsArchiveWithFilters.txt"
FILE_NEWS_ARCHIVE_EMPTY = "newsArchive/newsArchiveEmpty.txt"
FILE_NEWS_ARCHIVE_ERROR = "newsArchive/newsArchiveError.txt"
FILE_NEWS_NOT_FOUND = "news/newsNotFound.txt"
FILE_NEWS_ARTICLE = "news/newsPostWithDiscussionThread.txt"
FILE_NEWS_TICKER = "news/newsTicker.txt"
FILE_NEWS_FEATURED_ARTICLE = "news/newsFeaturedArticle.txt"


class TestNews(TestCommons):

    # region News Archive Tests
    def test_news_archive_parser_from_content_initial(self):
        """Test parsing the news archive initial page."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_INITIAL)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertIsInstance(news_archive, NewsArchive)
        self.assertEqual(datetime.date(2023, 3, 16), news_archive.from_date)
        self.assertEqual(datetime.date(2023, 4, 15), news_archive.to_date)
        self.assertSizeEquals(news_archive.types, 3)
        self.assertSizeEquals(news_archive.categories, 5)
        self.assertIsNotNone(news_archive.url)

    def test_news_archive_parser_from_content_with_results_filtered(self):
        """Testing parsing the news archive with results."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_RESULTS_FILTERED)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertEqual(datetime.date(2019, 3, 25), news_archive.from_date)
        self.assertEqual(datetime.date(2019, 5, 25), news_archive.to_date)
        self.assertSizeEquals(news_archive.types, 3)
        self.assertSizeEquals(news_archive.categories, 5)
        news_list = news_archive.entries
        self.assertIsNotEmpty(news_list)
        latest_news = news_list[0]
        self.assertIsInstance(latest_news, NewsEntry)
        self.assertIsInstance(latest_news.id, int)
        self.assertIsInstance(latest_news.category, NewsCategory)
        self.assertIsInstance(latest_news.type, NewsType)
        self.assertIsInstance(latest_news.published_on, datetime.date)
        self.assertIsNotNone(latest_news.url)
        self.assertEqual(latest_news.url, get_news_url(latest_news.id))

    def test_news_archive_parser_from_content_empty(self):
        """Testing parsing a news article that doesn't exist"""
        content = self.load_resource(FILE_NEWS_ARCHIVE_EMPTY)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertEqual(datetime.date(2023, 4, 13), news_archive.from_date)
        self.assertEqual(datetime.date(2023, 4, 15), news_archive.to_date)
        self.assertIsEmpty(news_archive.entries)

    def test_news_archive_parser_from_content_error(self):
        """Testing parsing the news archive resulting in an error message."""
        content = self.load_resource(FILE_NEWS_ARCHIVE_ERROR)

        news_archive = NewsArchiveParser.from_content(content)

        self.assertIsInstance(news_archive, NewsArchive)
        self.assertEqual(datetime.date(2019, 3, 25), news_archive.from_date)
        self.assertEqual(datetime.date(2018, 5, 25), news_archive.to_date)
        self.assertIsEmpty(news_archive.entries)

    def test_news_archive_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            NewsArchiveParser.from_content(content)

    # endregion

    # region News Tests

    def test_news_parser_from_content_not_found(self):
        """Testing parsing an empty news article"""
        content = self.load_resource(FILE_NEWS_NOT_FOUND)

        news = NewsParser.from_content(content)

        self.assertIsNone(news)

    def test_news_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            NewsParser.from_content(content)

    def test_news_parser_from_content_ticker(self):
        """Testing parsing a news ticker"""
        content = self.load_resource(FILE_NEWS_TICKER)
        news = NewsParser.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(NewsCategory.DEVELOPMENT, news.category)
        self.assertIsInstance(news.published_on, datetime.date)
        self.assertEqual("News Ticker", news.title)
        self.assertIsNone(news.thread_id)

    def test_news_parser_from_content_post_with_discussion_thread(self):
        """Testing parsing an article"""
        content = self.load_resource(FILE_NEWS_ARTICLE)
        news = NewsParser.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(news.category, NewsCategory.DEVELOPMENT)
        self.assertIsInstance(news.published_on, datetime.date)
        self.assertEqual(news.title, "Sign Up for the VANGUARD Tournament")
        self.assertEqual(news.thread_id, 4725194)
        self.assertIsNotNone(news.thread_url)

    def test_news_parser_from_content_article(self):
        """Testing parsing an article"""
        content = self.load_resource(FILE_NEWS_FEATURED_ARTICLE)
        news = NewsParser.from_content(content)

        self.assertIsInstance(news, News)
        self.assertEqual(NewsCategory.COMMUNITY, news.category, )
        self.assertIsInstance(news.published_on, datetime.date)
        self.assertEqual("Tibian Letters Part II", news.title)
        self.assertEqual(4952487, news.thread_id)
        self.assertIsNotNone(news.thread_url)

    # endregion
