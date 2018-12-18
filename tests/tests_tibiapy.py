import os.path
import unittest

import tibiapy

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")


class TestTibiaPy(unittest.TestCase):
    FILE_UNRELATED_SECTION = "tibiacom_about.txt"

    @staticmethod
    def _load_resource(resource):
        with open(os.path.join(RESOURCES_PATH, resource)) as f:
            return f.read()

    # This uses a static method fom Guild class, so it should only be used for Guild
    @staticmethod
    def _get_parsed_content(resource, beautiful_soup=True):
        content = TestTibiaPy._load_resource(resource)
        return tibiapy.Guild._beautiful_soup(content) if beautiful_soup else content
