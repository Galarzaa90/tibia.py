import datetime

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Character
from tibiapy.utils import parse_tibia_datetime

PATH_CHARACTER_RESOURCE = "character_regular.txt"
FILE_CHARACTER_NOT_FOUND = "character_not_found.txt"
FILE_CHARACTER_FORMER_NAMES = "character_former_names.txt"
FILE_CHARACTER_DELETION = "character_deletion.txt"
FILE_CHARACTER_DEATHS_COMPLEX = "character_deaths_complex.txt"


class TestCharacter(TestTibiaPy):
    def testGuilds(self):
        character = Character.from_content(self._get_parsed_content(PATH_CHARACTER_RESOURCE, False))
        self._compare_character(Character("Tschas", "Gladera", "Druid", 205, "female"), character)
        self.assertIsNotNone(character.guild_membership)
        self.assertEqual("Redd Alliance", character.guild_membership["guild"])
        self.assertEqual("Mentor", character.guild_membership["rank"])
        self.assertEqual(character.guild_name, character.guild_membership["guild"])
        self.assertEqual(character.guild_rank, character.guild_membership["rank"])
        self.assertEqual("Free Account", character.account_status)
        self.assertEqual(139, character.achievement_points)
        self.assertIsNone(character.house)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(0, character.deaths.__len__())
        self.assertEqual(parse_tibia_datetime("Apr 22 2018, 16:00:38 CEST"), character.last_login)
        self.assertEqual(character.url, Character.get_url(character.name))

    def _compare_character(self, mock_character, character):
        self.assertEqual(mock_character.name, character.name)
        self.assertEqual(mock_character.world, character.world)
        self.assertEqual(mock_character.vocation, character.vocation)
        self.assertEqual(mock_character.level, character.level)
        self.assertEqual(mock_character.sex, character.sex)

    def testCharacterNotFound(self):
        content = self._load_resource(FILE_CHARACTER_NOT_FOUND)
        char = Character.from_content(content)
        self.assertIsNone(char)

    def testCharacterFormerNames(self):
        content = self._load_resource(FILE_CHARACTER_FORMER_NAMES)
        char = Character.from_content(content)
        self.assertIsInstance(char.former_names, list)
        self.assertTrue(char.former_names)
        self.assertEqual(len(char.former_names), 2)

    def testCharacterDeletion(self):
        content = self._load_resource(FILE_CHARACTER_DELETION)
        char = Character.from_content(content)
        self.assertEqual("Expendable Dummy", char.name)
        self.assertIsNotNone(char.deletion_date)
        self.assertIsInstance(char.deletion_date, datetime.datetime)

    def testCharacterComplexDeaths(self):
        content = self._load_resource(FILE_CHARACTER_DEATHS_COMPLEX)
        parsed_content = Character._beautiful_soup(content)
        tables = Character._parse_tables(parsed_content)
        self.assertTrue("Character Deaths" in tables.keys())
        char = {}
        Character._parse_deaths(char, tables["Character Deaths"])