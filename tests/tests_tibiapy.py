import unittest
import os.path

from tibiapy import Guild

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")


class TestTibiaPy(unittest.TestCase):

    @staticmethod
    def _get_parsed_content(resource, beautiful_soup=True):
        with open(RESOURCES_PATH + resource) as f:
            content = f.read()
        return Guild._beautiful_soup(content) if beautiful_soup else content
