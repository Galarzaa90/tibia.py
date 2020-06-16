import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature, ForumBoard, InvalidContent, LastPost, ListedBoard, ListedThread

FILE_WORLD_BOARDS = "forums/tibiacom_section.txt"
FILE_SECTION_EMPTY_BOARD = "forums/tibiacom_section_empty_board.txt"
FILE_SECTION_EMPTY = "forums/tibiacom_section_empty.txt"
FILE_BOARD_THREAD_LIST = "forums/tibiacom_board.txt"
FILE_BOARD_EMPTY_THREAD_LIST = "forums/tibiacom_board_empty.txt"
FILE_BOARD_INVALID_PAGE = "forums/tibiacom_board_invalid_page.txt"


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
