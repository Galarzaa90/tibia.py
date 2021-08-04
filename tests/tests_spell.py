import unittest

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
        spell = SpellsSection.from_content(content)

    def test_spell_from_content_rune(self):
        """"""
        content = self.load_resource(FILE_SPELL_RUNE)
        spell = Spell.from_content(content)

    def test_spell_from_content_secondary_group(self):
        """"""
        content = self.load_resource(FILE_SPELL_SECONDARY_GROUP)
        spell = Spell.from_content(content)

    # endregion
