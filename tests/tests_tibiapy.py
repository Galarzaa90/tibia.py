import os.path
import unittest
from typing import Sized

import tibiapy

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")


class TestCommons(unittest.TestCase):
    FILE_UNRELATED_SECTION = "tibiacom_about.txt"


    def assertIsEmpty(self, collection: Sized, msg = None):
        self.assertEqual(0, len(collection), msg)

    def assertIsNotEmpty(self, collection: Sized, msg = None):
        self.assertGreater(len(collection), 0, msg)

    def assertSizeEquals(self, collection: Sized, size: int, msg = None):
        self.assertEqual(size, len(collection), msg)

    @staticmethod
    def load_resource(resource):
        with open(os.path.join(RESOURCES_PATH, resource)) as f:
            return f.read()

    @staticmethod
    def load_parsed_resource(resource):
        content = TestCommons.load_resource(resource)
        return tibiapy.utils.parse_tibiacom_content(content)

