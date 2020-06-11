import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature, ForumBoard, InvalidContent, LastPost, ListedBoard

FILE_WORLD_BOARDS = "forums/tibiacom_world_boards.txt"
FILE_BOARD_THREAD_LIST = "forums/tibiacom_thread_list.txt"


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

    def test_forum_board_from_content(self):
        content = self._load_resource(FILE_BOARD_THREAD_LIST)

        boards = ForumBoard.from_content(content)