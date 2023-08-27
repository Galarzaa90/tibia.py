import contextlib
import os.path
import unittest
from typing import Callable, Iterable, Sized, TypeVar

import tibiapy

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")

T = TypeVar("T")


class TestCommons(unittest.TestCase):
    FILE_UNRELATED_SECTION = "aboutSection.txt"

    def assertIsEmpty(self, collection: Sized, msg=None):
        self.assertEqual(0, len(collection), msg)

    def assertIsNotEmpty(self, collection: Sized, msg=None):
        self.assertGreater(len(collection), 0, msg)

    def assertSizeEquals(self, collection: Sized, size: int, msg=None):
        self.assertEqual(size, len(collection), msg)

    def assertSizeAtLeast(self, collection: Sized, size: int, msg=None):
        self.assertGreaterEqual(len(collection), size, msg)

    def assertForAtLeast(self, collection: Iterable[T], n: int, test: Callable[[T], None], msg=None):
        pass_count = 0
        for item in collection:
            with contextlib.suppress(AssertionError):
                test(item)
                pass_count += 1
        if pass_count < n:
            self.fail(self._formatMessage(msg, f"Expected at least {n} to pass, {pass_count} passed."))

    def assertForAll(self, collection: Iterable[T], test: Callable[[T], None], msg=None):
        for item in collection:
            try:
                test(item)
            except AssertionError as ae:
                raise self.fail(self._formatMessage(msg, f"Expected all to pass: {ae}"))

    def assertForAtLeastOne(self, collection: Iterable[T], test: Callable[[T], None], msg=None):
        self.assertForAtLeast(collection, 1, test, msg)

    @staticmethod
    def load_resource(resource):
        with open(os.path.join(RESOURCES_PATH, resource)) as f:
            return f.read()

    @staticmethod
    def load_parsed_resource(resource):
        content = TestCommons.load_resource(resource)
        return tibiapy.utils.parse_tibiacom_content(content)
