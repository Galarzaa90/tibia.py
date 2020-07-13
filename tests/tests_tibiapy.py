import os.path

import tibiapy

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")


class TestCommons:
    FILE_UNRELATED_SECTION = "tibiacom_about.txt"

    @staticmethod
    def load_resource(resource):
        with open(os.path.join(RESOURCES_PATH, resource)) as f:
            return f.read()

    @staticmethod
    def load_parsed_resource(resource):
        content = TestCommons.load_resource(resource)
        return tibiapy.utils.parse_tibiacom_content(content)
