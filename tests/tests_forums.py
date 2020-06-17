import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature, ForumAnnouncement, ForumBoard, ForumThread, InvalidContent, LastPost, ListedBoard, \
    ListedThread, \
    ThreadStatus

FILE_WORLD_BOARDS = "forums/tibiacom_section.txt"
FILE_SECTION_EMPTY_BOARD = "forums/tibiacom_section_empty_board.txt"
FILE_SECTION_EMPTY = "forums/tibiacom_section_empty.txt"
FILE_BOARD_THREAD_LIST = "forums/tibiacom_board.txt"
FILE_BOARD_EMPTY_THREAD_LIST = "forums/tibiacom_board_empty.txt"
FILE_BOARD_INVALID_PAGE = "forums/tibiacom_board_invalid_page.txt"
FILE_BOARD_GOLDEN_FRAMES = "forums/tibiacom_board_golden_frame.txt"
FILE_ANNOUNCEMENT = "forums/tibiacom_announcement.txt"
FILE_ANNOUNCEMENT_NOT_FOUND = "forums/tibiacom_announcement_not_found.txt"
FILE_THREAD = "forums/tibiacom_thread.txt"


class TestForum(TestCommons, unittest.TestCase):
    def test_listed_board_list_from_content_world_boards(self):
        content = self._load_resource(FILE_WORLD_BOARDS)

        boards = ListedBoard.list_from_content(content)

        self.assertEqual(77, len(boards))
        for i, board in enumerate(boards):
            with self.subTest(i=i):
                self.assertIsInstance(board, ListedBoard)
                self.assertIsNotNone(board.name)
                self.assertGreater(board.board_id, 0)
                self.assertGreater(board.posts, 0)
                self.assertGreater(board.threads, 0)
                self.assertIsInstance(board.last_post, LastPost)

    def test_listed_board_list_from_content_empty_board(self):
        content = self._load_resource(FILE_SECTION_EMPTY_BOARD)

        boards = ListedBoard.list_from_content(content)

        self.assertEqual(77, len(boards))
        for i, board in enumerate(boards):
            with self.subTest(i=i):
                self.assertIsInstance(board, ListedBoard)
                self.assertIsNotNone(board.name)
                self.assertGreater(board.board_id, 0)
                self.assertGreaterEqual(board.posts, 0)
                self.assertGreaterEqual(board.threads, 0)

    def test_listed_board_list_from_content_empty_section(self):
        content = self._load_resource(FILE_SECTION_EMPTY)

        boards = ListedBoard.list_from_content(content)

        self.assertIsInstance(boards, list)

    def test_listed_board_list_from_content_unrelated_section(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ListedBoard.list_from_content(content)

    def test_forum_board_from_content(self):
        content = self._load_resource(FILE_BOARD_THREAD_LIST)

        board = ForumBoard.from_content(content)

        self.assertIsNotNone(board)
        self.assertEqual("Antica", board.name)
        self.assertEqual("World Boards", board.section)
        self.assertEqual(1, board.page)
        self.assertEqual(5, board.total_pages)
        self.assertEqual(25, board.board_id)
        self.assertEqual(30, len(board.threads))
        self.assertIsNotNone(board.next_page_url)
        self.assertEqual(board.next_page_url, ListedBoard.get_url(board.board_id, board.page+1, board.age))
        for i, thread in enumerate(board.threads):
            with self.subTest(i=i):
                self.assertIsInstance(thread, ListedThread)
                self.assertIsNotNone(thread.title)
                self.assertGreater(thread.thread_id, 0)
                self.assertGreaterEqual(thread.views, 0)
                self.assertGreaterEqual(thread.replies, 0)
                self.assertIsInstance(thread.last_post, LastPost)

    def test_forum_board_from_content_empty_threads(self):
        content = self._load_resource(FILE_BOARD_EMPTY_THREAD_LIST)

        board = ForumBoard.from_content(content)

        self.assertIsNotNone(board)
        self.assertEqual("Ysolera - Trade", board.name)
        self.assertEqual("Trade Boards", board.section)
        self.assertEqual(1, board.page)
        self.assertEqual(1, board.total_pages)
        self.assertEqual(146059, board.board_id)
        self.assertEqual(0, len(board.threads))
        self.assertIsNone(board.next_page_url)
        self.assertIsNone(board.previous_page_url)

    def test_forum_board_from_content_unrelated_section(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumBoard.from_content(content)

    def test_forum_board_from_content_invalid_page(self):
        content = self._load_resource(FILE_BOARD_INVALID_PAGE)

        board = ForumBoard.from_content(content)

        self.assertEqual("Antica", board.name)
        self.assertEqual("World Boards", board.section)
        self.assertEqual([], board.threads)
        self.assertEqual(0, board.board_id)

    def test_forum_board_from_content_golden_frame(self):
        content = self._load_resource(FILE_BOARD_GOLDEN_FRAMES)

        board = ForumBoard.from_content(content)

        self.assertEqual("Proposals (English Only)", board.name)
        self.assertEqual("Community Boards", board.section)
        self.assertEqual(30, len(board.threads))
        self.assertEqual(5, len(board.announcements))
        self.assertEqual(1798, board.total_pages)
        for i, thread in enumerate(board.threads):
            with self.subTest(i=i):
                self.assertTrue(thread.golden_frame)
                self.assertTrue(thread.status & ThreadStatus.HOT)
                self.assertTrue(thread.status & ThreadStatus.CLOSED)

    def test_forum_announcement_from_content(self):
        content = self._load_resource(FILE_ANNOUNCEMENT)

        announcement = ForumAnnouncement.from_content(content, 33)

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

    def test_forum_announcement_from_content_not_found(self):
        content = self._load_resource(FILE_ANNOUNCEMENT_NOT_FOUND)

        announcement = ForumAnnouncement.from_content(content, 34)

        self.assertIsNone(announcement)

    def test_forum_announcement_from_content_unrelated_section(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContent):
            ForumAnnouncement.from_content(content, 34)

    def test_forum_thread_from_content(self):
        content = self._load_resource(FILE_THREAD)

        thread = ForumThread.from_content(content)

        self.assertEqual("News: Team Finder, Visualisation of Loot Lists", thread.title)
        self.assertEqual(4797985,thread.thread_id)
        self.assertEqual('Auditorium (English Only)',thread.board)
        self.assertEqual('Community Boards', thread.section)
        self.assertEqual(4796826, thread.previous_topic_number)
        self.assertEqual(4797838, thread.next_topic_number)
        self.assertEqual(1, thread.page)
        self.assertEqual(9, thread.total_pages)
        self.assertEqual(20, len(thread.posts))

        post = thread.posts[0]
        self.assertEqual("Skerio", post.author.name)
        self.assertEqual("Relania", post.author.world)
        self.assertEqual("Community Manager", post.author.position)
        self.assertEqual(316, post.author.posts)
        self.assertEqual("Mirade", post.edited_by)
        self.assertTrue(post.golden_frame)
        self.assertEqual(38969385, post.post_id)
        self.assertIsNotNone(post.url)
