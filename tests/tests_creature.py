import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, CreaturesSection, Creature, CreatureEntry

FILE_CREATURE_SECTION = "library/creature_list.txt"
FILE_CREATURE_CONVINCEABLE = "library/creature_convinceable.txt"
FILE_CREATURE_ELEMENTAL_RESISTANCES = "library/creature_elemental_resistances.txt"


class TestCreature(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_creatures_section_from_boosted_creature_header_content(self):
        """Testing parsing the boosted creture from any tibia.com page."""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        creature = CreaturesSection.boosted_creature_from_header(content)

        self.assertIsInstance(creature, CreatureEntry)
        self.assertEqual("Skeleton Warrior", creature.name)

    def test_creatures_section_from_boosted_creature_header_content_not_tibiacom(self):
        """Testing parsing the boosted creature from a page that is not Tibia.com"""
        with self.assertRaises(InvalidContent):
            CreaturesSection.boosted_creature_from_header("<html><div><p>Nothing</p></div></html>")

    def test_creature_section_from_content(self):
        """Test parsing the creatures section"""
        content = self.load_resource(FILE_CREATURE_SECTION)
        creatures = CreaturesSection.from_content(content)

        self.assertIsNotNone(creatures)
        self.assertIsNotNone(creatures.boosted_creature)
        self.assertEqual("Blood Crab", creatures.boosted_creature.name)
        self.assertEqual("bloodcrab", creatures.boosted_creature.identifier)
        self.assertIsNotNone(creatures.boosted_creature.image_url)
        self.assertIsNotNone(creatures.boosted_creature.url)
        self.assertEqual(536, len(creatures.creatures))
        for creature in creatures.creatures:
            with self.subTest(name=creature.name):
                self.assertIsInstance(creature.name, str)
                self.assertIsInstance(creature.identifier, str)

    def test_creatures_section_from_content_invalid_content(self):
        """Testing parsing the creatures section from an invalid section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CreaturesSection.from_content(content)

    def test_creature_from_content(self):
        content = self.load_resource(FILE_CREATURE_CONVINCEABLE)
        creature = Creature.from_content(content)

        self.assertIsNotNone(creature)
        self.assertEqual("Fish", creature.name)
        self.assertEqual("fish", creature.identifier)
        self.assertEqual(25, creature.hitpoints)
        self.assertEqual(0, creature.experience)
        self.assertEqual(0, creature.mana_cost)
        self.assertFalse(creature.summonable)
        self.assertTrue(creature.convinceable)
        self.assertEqual("nothing", creature.loot)

    def test_creature_from_content_elemental_resistances(self):
        content = self.load_resource(FILE_CREATURE_ELEMENTAL_RESISTANCES)
        creature = Creature.from_content(content)

        self.assertIsNotNone(creature)
        self.assertEqual("Dragons", creature.name)
        self.assertEqual("dragon", creature.identifier)
        self.assertEqual(1000, creature.hitpoints)
        self.assertEqual(700, creature.experience)
        self.assertIsNone(creature.mana_cost)
        self.assertFalse(creature.summonable)
        self.assertFalse(creature.convinceable)
        self.assertIsNotNone(creature.description)
        self.assertIn("energy", creature.strong_against)
        self.assertIn("fire", creature.immune_to)
        self.assertIn("ice", creature.weak_against)

    def test_creature_from_content_invalid_content(self):
        """Testing parsing the creatures section from an invalid section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        creature = Creature.from_content(content)

        self.assertIsNone(creature)
    # endregion
