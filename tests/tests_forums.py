import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, ThreadStatus
from tibiapy.models import BoardEntry, LastPost, ThreadEntry, CMPostArchive
from tibiapy.models.forum import BasePost, ForumSection
from tibiapy.parsers.forum import ForumBoardParser, ForumAnnouncementParser, ForumThreadParser, \
    CMPostArchiveParser, ForumSectionParser
from tibiapy.urls import get_forum_board_url, get_cm_post_archive_url

FILE_WORLD_BOARDS = "forums/tibiacom_section.txt"
FILE_SECTION_EMPTY_BOARD = "forums/forum_section_with_empty_board.txt"
FILE_SECTION_EMPTY = "forums/tibiacom_section_empty.txt"
FILE_BOARD_THREAD_LIST = "forums/tibiacom_board.txt"
FILE_BOARD_EMPTY_THREAD_LIST = "forums/tibiacom_board_empty.txt"
FILE_BOARD_INVALID_PAGE = "forums/tibiacom_board_invalid_page.txt"
FILE_BOARD_GOLDEN_FRAMES = "forums/tibiacom_board_golden_frame.txt"
FILE_ANNOUNCEMENT = "forums/tibiacom_announcement.txt"
FILE_ANNOUNCEMENT_NOT_FOUND = "forums/tibiacom_announcement_not_found.txt"
FILE_THREAD = "forums/tibiacom_thread.txt"
FILE_THREAD_NOT_FOUND = "forums/tibiacom_thread_not_found.txt"
FILE_THREAD_INVALID_PAGE = "forums/tibiacom_thread_invalid_page.txt"
FILE_CM_POST_ARCHIVE_INITIAL = "forums/tibiacom_cmpostarchive_initial.txt"
FILE_CM_POST_ARCHIVE_NO_PAGES = "forums/tibiacom_cmpostarchive_no_pages.txt"
FILE_CM_POST_ARCHIVE_NO_RESULTS = "forums/tibiacom_cmpostarchive_no_results.txt"
FILE_CM_POST_ARCHIVE_PAGES = "forums/tibiacom_cmpostarchive_pages.txt"


class TestForum(TestCommons):
    def test_forum_section_parser_from_content_world_boards(self):
        content = self.load_resource(FILE_WORLD_BOARDS)

        forum_section = ForumSectionParser.from_content(content)

        self.assertEqual(2, forum_section.section_id)
        self.assertEqual(82, len(forum_section.entries))
        for i, board in enumerate(forum_section.entries):
            with self.subTest(i=i):
                self.assertIsInstance(board, BoardEntry)
                self.assertIsNotNone(board.name)
                self.assertGreater(board.board_id, 0)
                self.assertGreater(board.posts, 0)
                self.assertGreater(board.threads, 0)
                self.assertIsInstance(board.last_post, LastPost)

    def test_forum_section_parser_from_content_empty_board(self):
        content = self.load_resource(FILE_SECTION_EMPTY_BOARD)

        forum_section = ForumSectionParser.from_content(content)

        self.assertEqual(3, forum_section.section_id)
        self.assertEqual(90, len(forum_section.entries))
        for i, board in enumerate(forum_section.entries):
            with self.subTest(i=i):
                self.assertIsInstance(board, BoardEntry)
                self.assertIsNotNone(board.name)
                self.assertGreater(board.board_id, 0)
                self.assertGreaterEqual(board.posts, 0)
                self.assertGreaterEqual(board.threads, 0)
                self.assertIsNotNone(board.url)

    def test_forum_section_parser_from_content_empty_section(self):
        content = self.load_resource(FILE_SECTION_EMPTY)

        forum_section = ForumSectionParser.from_content(content)

        self.assertEqual(10, forum_section.section_id)
        self.assertIsInstance(forum_section, ForumSection)
        self.assertEqual(0, len(forum_section.entries))

    def test_forum_section_parser_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumSectionParser.from_content(content)

    def test_forum_board_from_content(self):
        content = self.load_resource(FILE_BOARD_THREAD_LIST)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)
        self.assertEqual("Antica", board.name)
        self.assertEqual("World Boards", board.section)
        self.assertEqual(1, board.current_page)
        self.assertEqual(2, board.total_pages)
        self.assertEqual(25, board.board_id)
        self.assertEqual(30, len(board.entries))
        self.assertIsNotNone(board.url)
        self.assertIsNotNone(board.next_page_url)
        self.assertEqual(board.next_page_url, get_forum_board_url(board.board_id, board.current_page + 1, board.age))
        for i, thread in enumerate(board.entries):
            with self.subTest(i=i):
                self.assertIsInstance(thread, ThreadEntry)
                self.assertIsNotNone(thread.title)
                self.assertGreater(thread.thread_id, 0)
                self.assertGreaterEqual(thread.views, 0)
                self.assertGreaterEqual(thread.replies, 0)
                self.assertIsInstance(thread.last_post, LastPost)
                self.assertIsNotNone(thread.last_post.author_url)

        with self.assertRaises(ValueError):
            board.get_page_url(-1)

    def test_board_section_urls(self):
        self.assertIsNotNone(BoardEntry.get_community_boards_url())
        self.assertIsNotNone(BoardEntry.get_support_boards_url())
        self.assertIsNotNone(BoardEntry.get_world_boards_url())
        self.assertIsNotNone(BoardEntry.get_trade_boards_url())

    def test_forum_board_from_content_empty_threads(self):
        content = self.load_resource(FILE_BOARD_EMPTY_THREAD_LIST)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)
        self.assertEqual("Role Playing", board.name)
        self.assertEqual("Community Boards", board.section)
        self.assertEqual(1, board.current_page)
        self.assertEqual(1, board.total_pages)
        self.assertEqual(11, board.board_id)
        self.assertEqual(0, len(board.entries))
        self.assertIsNone(board.next_page_url)
        self.assertIsNone(board.previous_page_url)

    def test_forum_board_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumBoardParser.from_content(content)

    def test_forum_board_from_content_invalid_page(self):
        content = self.load_resource(FILE_BOARD_INVALID_PAGE)

        board = ForumBoardParser.from_content(content)

        self.assertEqual("Antica", board.name)
        self.assertEqual("World Boards", board.section)
        self.assertEqual([], board.entries)
        self.assertEqual(0, board.board_id)

    def test_forum_board_from_content_golden_frame(self):
        content = self.load_resource(FILE_BOARD_GOLDEN_FRAMES)

        board = ForumBoardParser.from_content(content)

        self.assertEqual("Proposals (English Only)", board.name)
        self.assertEqual("Community Boards", board.section)
        self.assertEqual(30, len(board.entries))
        self.assertEqual(5, len(board.announcements))
        self.assertEqual(1893, board.total_pages)
        for i, thread in enumerate(board.entries):
            with self.subTest(i=i):
                self.assertTrue(thread.golden_frame)
                self.assertTrue(thread.status & ThreadStatus.HOT)
                self.assertTrue(thread.status & ThreadStatus.CLOSED)
                self.assertIsNotNone(thread.url)

    def test_forum_announcement_from_content(self):
        content = self.load_resource(FILE_ANNOUNCEMENT)

        announcement = ForumAnnouncementParser.from_content(content, 33)

        self.assertIsNotNone(announcement)
        self.assertEqual("Legal Disclaimer", announcement.title)
        self.assertEqual(33, announcement.announcement_id)
        self.assertEqual("Proposals (English Only)", announcement.board)
        self.assertEqual(10, announcement.board_id)
        self.assertEqual("Community Boards", announcement.section)
        self.assertEqual(12, announcement.section_id)
        self.assertIsNotNone(announcement.author)
        self.assertEqual("CM Mirade", announcement.author.name)
        self.assertEqual(2, announcement.author.level)
        self.assertEqual(159, announcement.author.posts)
        self.assertEqual("Vunira", announcement.author.world)
        self.assertEqual("Community Manager", announcement.author.position)
        self.assertIsNotNone(announcement.url)

    def test_forum_announcement_from_content_not_found(self):
        content = self.load_resource(FILE_ANNOUNCEMENT_NOT_FOUND)

        announcement = ForumAnnouncementParser.from_content(content, 34)

        self.assertIsNone(announcement)

    def test_forum_announcement_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumAnnouncementParser.from_content(content, 34)

    def test_forum_thread_from_content(self):
        content = self.load_resource(FILE_THREAD)

        thread = ForumThreadParser.from_content(content)

        self.assertEqual("News: Team Finder, Visualisation of Loot Lists", thread.title)
        self.assertEqual(4797985, thread.thread_id)
        self.assertEqual('Auditorium (English Only)', thread.board)
        self.assertEqual('Community Boards', thread.section)
        self.assertEqual(4796826, thread.previous_topic_number)
        self.assertEqual(4797838, thread.next_topic_number)
        self.assertEqual(1, thread.current_page)
        self.assertEqual(9, thread.total_pages)
        self.assertEqual(20, len(thread.entries))
        self.assertIsNotNone(thread.url)
        self.assertIsNone(thread.previous_page_url)
        self.assertIsNotNone(thread.next_page_url)
        self.assertIsNotNone(thread.previous_thread_url)
        self.assertIsNotNone(thread.next_thread_url)

        post = thread.entries[0]
        self.assertEqual("Skerio", post.author.name)
        self.assertEqual("Olima", post.author.world)
        self.assertEqual("Community Manager", post.author.position)
        self.assertEqual(872, post.author.posts)
        self.assertEqual("Mirade", post.edited_by)
        self.assertTrue(post.golden_frame)
        self.assertEqual(38969385, post.post_id)
        self.assertIsNotNone(post.url)

        with self.assertRaises(ValueError):
            thread.get_page_url(-1)

    def test_forum_thread_from_content_invalid_page(self):
        content = self.load_resource(FILE_THREAD_INVALID_PAGE)

        thread = ForumThreadParser.from_content(content)

        self.assertEqual("News: Te...", thread.title)
        self.assertEqual(0, thread.thread_id)
        self.assertEqual('Auditorium (English Only)', thread.board)
        self.assertEqual('Community Boards', thread.section)
        self.assertIsNone(thread.previous_topic_number)
        self.assertIsNone(thread.next_topic_number)
        self.assertEqual(1, thread.current_page)
        self.assertEqual(1, thread.total_pages)
        self.assertEqual(0, len(thread.entries))

    def test_forum_thread_from_content_not_found(self):
        content = self.load_resource(FILE_THREAD_NOT_FOUND)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNone(thread)

    def test_forum_thread_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumThreadParser.from_content(content)

    def test_cm_post_archive_from_content_initial(self):
        content = self.load_resource(FILE_CM_POST_ARCHIVE_INITIAL)

        cm_post_archive = CMPostArchiveParser.from_content(content)

        self.assertIsNotNone(cm_post_archive)
        self.assertEqual(0, cm_post_archive.results_count)
        self.assertEqual(1, cm_post_archive.current_page)
        self.assertEqual(1, cm_post_archive.total_pages)

    def test_cm_post_archive_from_content_no_pages(self):
        content = self.load_resource(FILE_CM_POST_ARCHIVE_NO_PAGES)

        cm_post_archive = CMPostArchiveParser.from_content(content)

        self.assertIsNotNone(cm_post_archive)
        self.assertEqual(5, cm_post_archive.results_count)
        self.assertEqual(1, cm_post_archive.current_page)
        self.assertEqual(1, cm_post_archive.total_pages)
        self.assertEqual(cm_post_archive.results_count, len(cm_post_archive.entries))

        post = cm_post_archive.entries[0]
        self.assertIsInstance(post, BasePost)
        self.assertEqual('Auditorium (English Only)', post.board)
        self.assertEqual(38974254, post.post_id)
        self.assertEqual('Ticker Messages June 2020', post.thread_title)

    def test_cm_post_archive_from_content_no_results(self):
        content = self.load_resource(FILE_CM_POST_ARCHIVE_NO_RESULTS)

        cm_post_archive = CMPostArchiveParser.from_content(content)

        self.assertIsNotNone(cm_post_archive)
        self.assertEqual(0, cm_post_archive.results_count)
        self.assertEqual(1, cm_post_archive.current_page)
        self.assertEqual(1, cm_post_archive.total_pages)
        self.assertEqual(cm_post_archive.results_count, len(cm_post_archive.entries))

    def test_cm_post_archive_from_content_pages(self):
        content = self.load_resource(FILE_CM_POST_ARCHIVE_PAGES)

        cm_post_archive = CMPostArchiveParser.from_content(content)

        self.assertIsNotNone(cm_post_archive)
        self.assertIsNotNone(cm_post_archive.url)
        self.assertIsNotNone(cm_post_archive.previous_page_url)
        self.assertIsNone(cm_post_archive.next_page_url)
        self.assertEqual(8370, cm_post_archive.results_count)
        self.assertEqual(168, cm_post_archive.current_page)
        self.assertEqual(168, cm_post_archive.total_pages)
        self.assertEqual(20, len(cm_post_archive.entries))

    def test_cm_post_archive_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CMPostArchiveParser.from_content(content)

    def test_cm_post_archive_get_page_url_negative_page(self):
        with self.assertRaises(ValueError):
            cmpost_archive = CMPostArchive()
            cmpost_archive.get_page_url(-1)

    def test_cm_post_archive_get_url_missing_parameter(self):
        with self.assertRaises(TypeError):
            get_cm_post_archive_url(None, datetime.date.today())
        with self.assertRaises(TypeError):
            get_cm_post_archive_url(datetime.date.today(), None)

    def test_cm_post_archive_get_url_invalid_dates(self):
        with self.assertRaises(ValueError):
            get_cm_post_archive_url(datetime.date.today(), datetime.date.today()-datetime.timedelta(days=20))

    def test_cm_post_archive_get_url_invalid_page(self):
        with self.assertRaises(ValueError):
            get_cm_post_archive_url(datetime.date.today()-datetime.timedelta(days=20), datetime.date.today(), -2)
