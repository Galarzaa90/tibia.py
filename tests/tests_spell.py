import tibiapy
from tests.tests_tibiapy import TestCommons
from tibiapy.parsers.spell import SpellsSectionParser, SpellParser

FILE_SPELLS_SECTION = "spellsSection/spellsSectionDefault.txt"
FILE_SPELLS_SECTION_EMPTY = "spellsSection/spellsSectionEmpty.txt"
FILE_SPELL = "spells/spell.txt"
FILE_SPELL_RUNE = "spells/spellWithRune.txt"
FILE_SPELL_REVELATION_PERK = "spells/spellRevelationPerk.txt"
FILE_SPELL_VARIABLE_MANA = "spells/spellVariableMana.txt"
FILE_SPELL_MULTILINE_DESC = "spells/spellMultilineDescription.txt"
FILE_SPELL_SECONDARY_GROUP = "spells/spellWithSecondaryGroup.txt"


class TestSpell(TestCommons,):
    # region Spells Section Tests

    def test_spells_section_parser_from_content(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(FILE_SPELLS_SECTION)

        spells_section = SpellsSectionParser.from_content(content)

        self.assertIsNotNone(spells_section)
        self.assertIsNotNone(spells_section.url)
        self.assertSizeEquals(spells_section.entries, 152)


    def test_spells_section_parser_from_content_no_results(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(FILE_SPELLS_SECTION_EMPTY)

        spells_section = SpellsSectionParser.from_content(content)

        self.assertIsEmpty(spells_section.entries)

    def test_spells_section_parser_from_content_unrelated_section(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(tibiapy.InvalidContentError):
            SpellsSectionParser.from_content(content)

    # endregion

    # region Spells Tests

    def test_spell_parser_from_content(self):
        content = self.load_resource(FILE_SPELL)

        spell = SpellParser.from_content(content)

        self.assertIsNotNone(spell)
        self.assertIsNotNone(spell.url)
        self.assertIsNotNone(spell.image_url)

        self.assertEqual("Light Healing", spell.name)
        self.assertEqual("exura", spell.words)
        self.assertIn("Druid", spell.vocations)
        self.assertEqual("Healing", spell.group.value)
        self.assertEqual("Instant", spell.spell_type.value)
        self.assertEqual(1, spell.cooldown)
        self.assertEqual(1, spell.cooldown_group)
        self.assertEqual(8, spell.exp_level)
        self.assertEqual(20, spell.mana)
        self.assertEqual(0, spell.price)
        self.assertIn("Carlin", spell.cities)
        self.assertFalse(spell.is_premium)

    def test_spell_parser_from_content_variable_mana(self):
        content = self.load_resource(FILE_SPELL_VARIABLE_MANA)

        spell = SpellParser.from_content(content)

        self.assertIsNone(spell.mana)

    def test_spell_parser_from_content_multiline_description(self):
        content = self.load_resource(FILE_SPELL_MULTILINE_DESC)

        spell = SpellParser.from_content(content)

        self.assertEqual(2, spell.description.count("\n"))

    def test_spell_parser_from_content_rune(self):
        """Testing parsing a rune spell."""
        content = self.load_resource(FILE_SPELL_RUNE)

        spell = SpellParser.from_content(content)

        self.assertEqual("Sudden Death Rune", spell.name)
        self.assertEqual("Support", spell.group.value)
        self.assertEqual("Rune", spell.spell_type.value)
        self.assertEqual(5, spell.soul_points)
        self.assertEqual("Sudden Death Rune", spell.rune.name)
        self.assertIn("Knight", spell.rune.vocations)
        self.assertEqual("Attack", spell.rune.group.value)
        self.assertEqual("Death", spell.rune.magic_type)
        self.assertEqual(45, spell.rune.exp_level)
        self.assertEqual(15, spell.rune.magic_level)

    def test_spell_parser_from_content_secondary_group(self):
        """Testing parsing a spell with a secondary group."""
        content = self.load_resource(FILE_SPELL_SECONDARY_GROUP)
        spell = SpellParser.from_content(content)

        self.assertIsNotNone(spell)
        self.assertEqual("Support", spell.group.value)
        self.assertEqual("Focus", spell.group_secondary)
        self.assertEqual(2, spell.cooldown)
        self.assertEqual(2, spell.cooldown_group)
        self.assertEqual(2, spell.cooldown_group_secondary)

    def test_spell_parser_from_content_revelation_perk(self):
        """Testing parsing a spell with a secondary group."""
        content = self.load_resource(FILE_SPELL_REVELATION_PERK)
        spell = SpellParser.from_content(content)

        self.assertIsNotNone(spell)
        self.assertIsNone(spell.exp_level)
        self.assertEqual(0, spell.price)
        self.assertIsEmpty(spell.cities)

    def test_spells_from_content_unknown_spell(self):
        """Testing parsing an unknown spell

        When trying to fetch a spell that doesn't exist, the website will just show the spells section.
        """
        content = self.load_resource(FILE_SPELLS_SECTION)
        spell = SpellParser.from_content(content)

        self.assertIsNone(spell)

    def test_spells_from_content_unrelated_section(self):
        """Testing parsing a boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(tibiapy.InvalidContentError):
            SpellParser.from_content(content)

    # endregion
