import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature, InvalidContent


class TestCreature(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_creature_from_content(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        creature = BoostedCreature.from_content(content)

        self.assertIsInstance(creature, BoostedCreature)
        self.assertEqual("Skeleton Warrior", creature.name)

    def test_creature_from_content_not_tibiacom(self):
        """Testing parsing a page that is not Tibia.com"""
        with self.assertRaises(InvalidContent):
            BoostedCreature.from_content("<html><div><p>Nothing</p></div></html>")

    # endregion
