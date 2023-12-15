import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.enums import ThreadStatus
from tibiapy.models import BoardEntry, CMPostArchive, ForumPost, LastPost, ThreadEntry
from tibiapy.parsers import (CMPostArchiveParser, ForumAnnouncementParser, ForumBoardParser, ForumSectionParser,
                             ForumThreadParser)
from tibiapy.urls import get_cm_post_archive_url, get_forum_board_url

FILE_WORLD_BOARDS = "forumSection/forumSection.txt"
FILE_SECTION_EMPTY_BOARD = "forumSection/forumSectionWithEmptyBoard.txt"
FILE_SECTION_EMPTY = "forumSection/forumSectionEmpty.txt"

FILE_BOARD_THREAD_LIST = "forumBoard/forumBoard.txt"
FILE_BOARD_WITH_ANNOUNCEMENTS = "forumBoard/forumBoardWithAnnouncements.txt"
FILE_BOARD_EMPTY_THREAD_LIST = "forumBoard/forumBoardEmpty.txt"
FILE_BOARD_INVALID_PAGE = "forumBoard/forumBoardInvalidPage.txt"
FILE_BOARD_GOLDEN_FRAMES = "forumBoard/forumBoardWithGoldenFrame.txt"
FILE_BOARD_THREAD_BY_DELETED_CHAR = "forumBoard/forumBoardWithThreadByDeletedChar.txt"
FILE_BOARD_THREAD_BY_TRADED_CHAR = "forumBoard/forumBoardWithThreadByTradedChar.txt"
FILE_BOARD_THREAD_LAST_POST_BY_DELETED_CHAR = "forumBoard/forumBoardWithThreadWithLastPostByDeletedChar.txt"
FILE_BOARD_THREAD_LAST_POST_BY_TRADED_CHAR = "forumBoard/forumBoardWithThreadWithLastPostByTradedChar.txt"
FILE_BOARD_NOT_FOUND = "forumBoard/forumBoardNotFound.txt"

FILE_ANNOUNCEMENT = "forumAnnouncement/forumAnnouncement.txt"
FILE_ANNOUNCEMENT_NOT_FOUND = "forumAnnouncement/forumAnnouncementNotFound.txt"

FILE_THREAD = "forumThread/forumThread.txt"
FILE_THREAD_NOT_FOUND = "forumThread/forumThreadNotFound.txt"
FILE_THREAD_INVALID_PAGE = "forumThread/forumThreadInvalidPage.txt"
FILE_THREAD_EDITED_POST = "forumThread/forumThreadWithEditedPost.txt"
FILE_THREAD_GOLDEN_FRAME = "forumThread/forumThreadWithGoldenFrame.txt"
FILE_THREAD_POST_BY_DELETED_CHAR = "forumThread/forumThreadWithPostByDeletedChar.txt"
FILE_THREAD_POST_BY_TRADED_CHAR = "forumThread/forumThreadWithPostByTradedChar.txt"
FILE_THREAD_POST_GOLDEN_FRAME = "forumThread/forumThreadWithPostWithGoldenFrame.txt"

FILE_CM_POST_ARCHIVE_INITIAL = "cmPostArchive/cmPostArchiveInitial.txt"
FILE_CM_POST_ARCHIVE_NO_PAGES = "cmPostArchive/cmPostArchiveNoPages.txt"
FILE_CM_POST_ARCHIVE_NO_RESULTS = "cmPostArchive/cmPostArchiveNoResults.txt"
FILE_CM_POST_ARCHIVE_PAGES = "cmPostArchive/cmPostArchivePages.txt"


class TestForum(TestCommons):

    # region Forum Section Tests

    def test_forum_section_parser_from_content_world_boards(self):
        content = self.load_resource(FILE_WORLD_BOARDS)

        forum_section = ForumSectionParser.from_content(content)

        self.assertEqual(2, forum_section.section_id)
        self.assertSizeEquals(forum_section.entries, 82)
        for board in forum_section.entries:
            self.assertIsNotNone(board.name)
            self.assertGreater(board.board_id, 0)
            self.assertGreater(board.posts, 0)
            self.assertGreater(board.threads, 0)
            self.assertIsInstance(board.last_post, LastPost)

    def test_forum_section_parser_from_content_empty_board(self):
        content = self.load_resource(FILE_SECTION_EMPTY_BOARD)

        forum_section = ForumSectionParser.from_content(content)

        def test_board_entry(board: BoardEntry):
            self.assertEqual(0, board.threads)
            self.assertEqual(0, board.posts)
            self.assertIsNone(board.last_post)

        self.assertForAtLeastOne(forum_section.entries, test_board_entry)

    def test_forum_section_parser_from_content_empty_section(self):
        content = self.load_resource(FILE_SECTION_EMPTY)

        forum_section = ForumSectionParser.from_content(content)

        self.assertIsEmpty(forum_section.entries)

    def test_forum_section_parser_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            ForumSectionParser.from_content(content)

    # endregion

    # region Forum Board Tests

    def test_forum_board_parser_from_content(self):
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

        with self.assertRaises(ValueError):
            board.get_page_url(-1)

    def test_forum_board_parser_from_content_with_announcements(self):
        content = self.load_resource(FILE_BOARD_WITH_ANNOUNCEMENTS)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)
        self.assertIsNotEmpty(board.announcements)

    def test_forum_board_parser_from_content_empty_threads(self):
        content = self.load_resource(FILE_BOARD_EMPTY_THREAD_LIST)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)
        self.assertEqual(0, board.results_count)
        self.assertEqual(1, board.total_pages)
        self.assertIsEmpty(board.entries)

    def test_forum_board_parser_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            ForumBoardParser.from_content(content)

    def test_forum_board_parser_from_content_invalid_page(self):
        content = self.load_resource(FILE_BOARD_INVALID_PAGE)

        board = ForumBoardParser.from_content(content)

        self.assertEqual("Antica", board.name)
        self.assertEqual("World Boards", board.section)
        self.assertEqual([], board.entries)
        self.assertEqual(0, board.board_id)

    def test_forum_board_parser_from_content_golden_frame(self):
        content = self.load_resource(FILE_BOARD_GOLDEN_FRAMES)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)

        def test_thread_entry(thread: ThreadEntry):
            self.assertTrue(thread.golden_frame)
            self.assertTrue(thread.status & ThreadStatus.HOT)
            self.assertTrue(thread.status & ThreadStatus.CLOSED)

        self.assertForAtLeastOne(board.entries, test_thread_entry)

    def test_forum_board_parser_from_content_thread_by_deleted_char(self):
        content = self.load_resource(FILE_BOARD_THREAD_BY_DELETED_CHAR)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)

        def test_thread_entry(thread: ThreadEntry):
            self.assertTrue(thread.thread_starter_deleted)

        self.assertForAtLeastOne(board.entries, test_thread_entry)

    def test_forum_board_parser_from_content_thread_by_traded_char(self):
        content = self.load_resource(FILE_BOARD_THREAD_BY_TRADED_CHAR)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)

        def test_thread_entry(thread: ThreadEntry):
            self.assertTrue(thread.thread_starter_traded)

        self.assertForAtLeastOne(board.entries, test_thread_entry)

    def test_forum_board_parser_from_content_thread_last_post_by_deleted_char(self):
        content = self.load_resource(FILE_BOARD_THREAD_LAST_POST_BY_DELETED_CHAR)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)

        def test_thread_entry(thread: ThreadEntry):
            self.assertIsNotNone(thread.last_post)
            self.assertTrue(thread.last_post.is_author_deleted)

        self.assertForAtLeastOne(board.entries, test_thread_entry)

    def test_forum_board_parser_from_content_thread_last_post_by_traded_char(self):
        content = self.load_resource(FILE_BOARD_THREAD_LAST_POST_BY_TRADED_CHAR)

        board = ForumBoardParser.from_content(content)

        self.assertIsNotNone(board)

        def test_thread_entry(thread: ThreadEntry):
            self.assertIsNotNone(thread.last_post)
            self.assertTrue(thread.last_post.is_author_traded)

        self.assertForAtLeastOne(board.entries, test_thread_entry)

    def test_forum_board_parser_from_content_not_found(self):
        content = self.load_resource(FILE_BOARD_NOT_FOUND)

        board = ForumBoardParser.from_content(content)

        self.assertIsNone(board)

    # endregion

    # region Forum Announcement Tests

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
        self.assertEqual(160, announcement.author.posts)
        self.assertEqual("Vunira", announcement.author.world)
        self.assertEqual("Community Manager", announcement.author.position)
        self.assertIsNotNone(announcement.url)

    def test_forum_announcement_from_content_not_found(self):
        content = self.load_resource(FILE_ANNOUNCEMENT_NOT_FOUND)

        announcement = ForumAnnouncementParser.from_content(content, 34)

        self.assertIsNone(announcement)

    def test_forum_announcement_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            ForumAnnouncementParser.from_content(content, 34)

    # endregion

    # region Forum Thread Tests

    def test_forum_thread_parser_from_content(self):
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

    def test_forum_thread_parser_from_content_invalid_page(self):
        content = self.load_resource(FILE_THREAD_INVALID_PAGE)

        thread = ForumThreadParser.from_content(content)

        self.assertEqual("News Tic...", thread.title)
        self.assertEqual(0, thread.thread_id)
        self.assertEqual('Auditorium (English Only)', thread.board)
        self.assertEqual('Community Boards', thread.section)
        self.assertIsNone(thread.previous_topic_number)
        self.assertIsNone(thread.next_topic_number)
        self.assertEqual(1, thread.current_page)
        self.assertEqual(1, thread.total_pages)
        self.assertEqual(0, len(thread.entries))

    def test_forum_thread_parser_from_content_with_edited_post(self):
        content = self.load_resource(FILE_THREAD_EDITED_POST)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNotNone(thread)

        def test_post(post: ForumPost):
            self.assertIsNotNone(post.edited_by)
            self.assertIsNotNone(post.edited_date)

        self.assertForAtLeastOne(thread.entries, test_post)

    def test_forum_thread_parser_from_content_with_golden_frame(self):
        content = self.load_resource(FILE_THREAD_GOLDEN_FRAME)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNotNone(thread)
        self.assertTrue(thread.golden_frame)

    def test_forum_thread_parser_from_content_with_post_by_deleted_char(self):
        content = self.load_resource(FILE_THREAD_POST_BY_DELETED_CHAR)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNotNone(thread)

        def test_post(post: ForumPost):
            self.assertIsNotNone(post.author.is_author_deleted)

        self.assertForAtLeastOne(thread.entries, test_post)

    def test_forum_thread_parser_from_content_with_post_by_traded_char(self):
        content = self.load_resource(FILE_THREAD_POST_BY_DELETED_CHAR)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNotNone(thread)

        def test_post(post: ForumPost):
            self.assertIsNotNone(post.author.is_author_traded)

        self.assertForAtLeastOne(thread.entries, test_post)

    def test_forum_thread_parser_from_content_with_post_with_golden_frame(self):
        content = self.load_resource(FILE_THREAD_POST_GOLDEN_FRAME)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNotNone(thread)

        def test_post(post: ForumPost):
            self.assertIsNotNone(post.golden_frame)

        self.assertForAtLeastOne(thread.entries, test_post)

    def test_forum_thread_parser_from_content_not_found(self):
        content = self.load_resource(FILE_THREAD_NOT_FOUND)

        thread = ForumThreadParser.from_content(content)

        self.assertIsNone(thread)

    def test_forum_thread_parser_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            ForumThreadParser.from_content(content)

    # endregion

    # region CM Post Archive Tests

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
        self.assertEqual(6, cm_post_archive.results_count)
        self.assertEqual(1, cm_post_archive.current_page)
        self.assertEqual(1, cm_post_archive.total_pages)
        self.assertEqual(cm_post_archive.results_count, len(cm_post_archive.entries))

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
        self.assertIsNone(cm_post_archive.previous_page_url)
        self.assertIsNotNone(cm_post_archive.next_page_url)
        self.assertEqual(738, cm_post_archive.results_count)
        self.assertEqual(1, cm_post_archive.current_page)
        self.assertEqual(15, cm_post_archive.total_pages)
        self.assertEqual(50, len(cm_post_archive.entries))

    def test_cm_post_archive_from_content_unrelated_section(self):
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
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
            get_cm_post_archive_url(datetime.date.today(), datetime.date.today() - datetime.timedelta(days=20))

    def test_cm_post_archive_get_url_invalid_page(self):
        with self.assertRaises(ValueError):
            get_cm_post_archive_url(datetime.date.today() - datetime.timedelta(days=20), datetime.date.today(), -2)

    # endregion
