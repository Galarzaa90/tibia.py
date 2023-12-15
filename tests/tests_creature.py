from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.models import CreatureEntry
from tibiapy.parsers import BoostableBossesParser, CreatureParser, CreaturesSectionParser

FILE_CREATURE_SECTION = "creaturesSection/creatureList.txt"
FILE_CREATURE_CONVINCEABLE = "creature/creatureConvinceable.txt"
FILE_CREATURE_ELEMENTAL_RESISTANCES = "creature/creatureElementalResistances.txt"
FILE_BOOSTABLE_BOSSES = "boostableBosses/bossList.txt"


class TestCreature(TestCommons):
    def test_creatures_section_from_boosted_creature_header_content(self):
        """Testing parsing the boosted creture from any tibia.com page."""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        creature = CreaturesSectionParser.boosted_creature_from_header(content)

        self.assertIsInstance(creature, CreatureEntry)
        self.assertEqual("Menacing Carnivor", creature.name)

    def test_creatures_section_from_boosted_creature_header_content_not_tibiacom(self):
        """Testing parsing the boosted creature from a page that is not Tibia.com"""
        with self.assertRaises(InvalidContentError):
            CreaturesSectionParser.boosted_creature_from_header("<html><div><p>Nothing</p></div></html>")

    def test_creature_section_from_content(self):
        """Test parsing the creatures section"""
        content = self.load_resource(FILE_CREATURE_SECTION)
        creatures = CreaturesSectionParser.from_content(content)

        self.assertIsNotNone(creatures)
        self.assertIsNotNone(creatures.boosted_creature)
        self.assertEqual(creatures.boosted_creature.name, "Mooh'tah Warrior")
        self.assertEqual(creatures.boosted_creature.identifier, "moohtahwarrior")
        self.assertIsNotNone(creatures.boosted_creature.image_url)
        self.assertIsNotNone(creatures.boosted_creature.url)
        self.assertSizeEquals(creatures.creatures, 609)
        for creature in creatures.creatures:
            self.assertIsInstance(creature.name, str)
            self.assertIsInstance(creature.identifier, str)

    def test_creatures_section_from_content_invalid_content(self):
        """Testing parsing the creatures section from an invalid section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            CreaturesSectionParser.from_content(content)

    def test_creature_from_content(self):
        content = self.load_resource(FILE_CREATURE_CONVINCEABLE)
        creature = CreatureParser.from_content(content)

        self.assertIsNotNone(creature)
        self.assertEqual(creature.name, "Fish")
        self.assertEqual(creature.identifier, "fish")
        self.assertEqual(creature.hitpoints, 25)
        self.assertEqual(creature.experience, 0)
        self.assertEqual(creature.mana_cost, 305)
        self.assertFalse(creature.summonable)
        self.assertTrue(creature.convinceable)
        self.assertEqual(creature.loot, "nothing")

    def test_creature_from_content_elemental_resistances(self):
        content = self.load_resource(FILE_CREATURE_ELEMENTAL_RESISTANCES)
        creature = CreatureParser.from_content(content)

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

        creature = CreatureParser.from_content(content)

        self.assertIsNone(creature)

    def test_boostable_bosses_from_content(self):
        """Test parsing the boostable bosses section"""
        content = self.load_resource(FILE_BOOSTABLE_BOSSES)
        bosses = BoostableBossesParser.from_content(content)

        self.assertIsNotNone(bosses)
        self.assertIsNotNone(bosses.boosted_boss)
        self.assertEqual("Tentugly", bosses.boosted_boss.name)
        self.assertEqual("fakeseamonster", bosses.boosted_boss.identifier)
        self.assertIsNotNone(bosses.boosted_boss.image_url)
        self.assertEqual(88, len(bosses.bosses))
        for boss in bosses.bosses:
            self.assertIsInstance(boss.name, str)
            self.assertIsInstance(boss.identifier, str)

    def test_boostable_bosses_from_content_invalid_content(self):
        """Testing parsing the creatures section from an invalid section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            BoostableBossesParser.from_content(content)


