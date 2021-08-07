import unittest

import tibiapy
from tests.tests_tibiapy import TestCommons
from tibiapy import Spell, SpellsSection

FILE_SPELLS_SECTION = "library/spell_list_default.txt"
FILE_SPELL_RUNE = "library/spell_rune.txt"
FILE_SPELL_SECONDARY_GROUP = "library/spell_secondary_group.txt"


class TestSpell(TestCommons, unittest.TestCase):
    # region Tibia.com Tests
    def test_spells_section_from_content(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(FILE_SPELLS_SECTION)
        spells_section = SpellsSection.from_content(content)

        self.assertIsNotNone(spells_section)
        self.assertEqual(141, len(spells_section.entries))

    def test_spells_section_from_content_unrelated_section(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(tibiapy.InvalidContent):
            spells_section = SpellsSection.from_content(content)

    def test_spell_from_content_rune(self):
        """Testing parsing a rune spell."""
        content = self.load_resource(FILE_SPELL_RUNE)
        spell = Spell.from_content(content)

        self.assertIsNotNone(spell)
        self.assertEqual("Chameleon Rune", spell.name)
        self.assertEqual("adevo ina", spell.words)
        self.assertIn("Druid", spell.vocations)
        self.assertEqual("Support", spell.group.value)
        self.assertEqual("Rune", spell.spell_type.value)
        self.assertEqual(2, spell.cooldown)
        self.assertEqual(2, spell.cooldown_group)
        self.assertEqual(2, spell.soul_points)
        self.assertEqual(1, spell.amount)
        self.assertEqual(27, spell.exp_level)
        self.assertEqual(600, spell.mana)
        self.assertEqual(1300, spell.price)
        self.assertIn("Thais", spell.cities)
        self.assertIn("Yalahar", spell.cities)
        self.assertIn("Edron", spell.cities)
        self.assertFalse(spell.premium)
        self.assertEqual("Chameleon Rune", spell.rune.name)
        self.assertIn("Knight", spell.rune.vocations)
        self.assertEqual("Support", spell.rune.group.value)
        self.assertEqual(27, spell.rune.exp_level)
        self.assertEqual(4, spell.rune.magic_level)

    def test_spell_from_content_secondary_group(self):
        """Testing parsing a spell with a secondary group."""
        content = self.load_resource(FILE_SPELL_SECONDARY_GROUP)
        spell = Spell.from_content(content)

        self.assertIsNotNone(spell)
        self.assertEqual("Protector", spell.name)
        self.assertEqual("utamo tempo", spell.words)
        self.assertIn("Knight", spell.vocations)
        self.assertEqual("Support", spell.group.value)
        self.assertEqual("Focus", spell.group_secondary)
        self.assertEqual("Instant", spell.spell_type.value)
        self.assertEqual(2, spell.cooldown)
        self.assertEqual(2, spell.cooldown_group)
        self.assertEqual(2, spell.cooldown_group_secondary)
        self.assertIsNone(spell.soul_points)
        self.assertIsNone(spell.amount)
        self.assertEqual(55, spell.exp_level)
        self.assertEqual(200, spell.mana)
        self.assertEqual(6000, spell.price)
        self.assertIn("Edron", spell.cities)
        self.assertTrue(spell.premium)

    def test_spells_from_content_unknown_spell(self):
        """Testing parsing an unknown spell

        When trying to fetch a spell that doesn't exist, the website will just show the spells section."""
        content = self.load_resource(FILE_SPELLS_SECTION)
        spell = Spell.from_content(content)

        self.assertIsNone(spell)

    def test_spells_from_content_unrelated_section(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(tibiapy.InvalidContent):
            spell = Spell.from_content(content)

    # endregion
