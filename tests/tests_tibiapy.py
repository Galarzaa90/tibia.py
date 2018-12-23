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

    @staticmethod
    def _load_parsed_resource(resource):
        content = TestTibiaPy._load_resource(resource)
        return tibiapy.utils.parse_tibiacom_content(content)

    def testSerializableGetItem(self):
        # Class inherits from Serializable
        world = tibiapy.World("Calmera")

        # Serializable allows accessing attributes like a dictionary
        self.assertEqual(world.name, world["name"])
        # And setting values too
        world["location"] = tibiapy.enums.WorldLocation.NORTH_AMERICA
        self.assertEqual(world.location, tibiapy.enums.WorldLocation.NORTH_AMERICA)

        # Accessing via __get__ returns KeyError instead of AttributeError to follow dictionary behaviour
        with self.assertRaises(KeyError):
            level = world["level"]  # NOSONAR

        # Accessing an undefined attribute that is defined in __slots__ returns `None` instead of raising an exception.
        del world.location
        self.assertIsNone(world["location"])

        # New attributes can't be created by assignation
        with self.assertRaises(KeyError):
            world["custom"] = "custom value"
