import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature, InvalidContent, ListedBoard

FILE_WORLD_BOARDS = "forums/tibiacom_world_boards.txt"

class TestForum(TestCommons, unittest.TestCase):
    def test_forum_from_content_world_boards(self):
        content = self._load_resource(FILE_WORLD_BOARDS)

        boards = ListedBoard.list_from_content(content)
        pass