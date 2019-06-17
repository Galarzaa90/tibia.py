import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import BoostedCreature


class TestCreature(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def testBoostedCreature(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        creature = BoostedCreature.from_content(content)

        self.assertIsInstance(creature, BoostedCreature)
        self.assertEqual("Skeleton Warrior", creature.name)

    # endregion
