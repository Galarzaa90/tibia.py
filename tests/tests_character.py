import datetime

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Character, Death, Killer
from tibiapy.utils import parse_tibia_datetime

FILE_CHARACTER_RESOURCE = "character_regular.txt"
FILE_CHARACTER_NOT_FOUND = "character_not_found.txt"
FILE_CHARACTER_FORMER_NAMES = "character_former_names.txt"
FILE_CHARACTER_DELETION = "character_deletion.txt"
FILE_CHARACTER_DEATHS_COMPLEX = "character_deaths_complex.txt"

FILE_CHARACTER_TIBIADATA = "character_tibiadata.txt"
FILE_CHARACTER_TIBIADATA_NOT_FOUND = "character_tibiadata_not_found.txt"


class TestCharacter(TestTibiaPy):
    def testGuilds(self):
        character = Character.from_content(self._get_parsed_content(FILE_CHARACTER_RESOURCE, False))
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
        self.assertEqual(parse_tibia_datetime("Oct 08 2018 22:17:00 CEST"), char.deletion_date)

    def testCharacterComplexDeaths(self):
        content = self._load_resource(FILE_CHARACTER_DEATHS_COMPLEX)
        char = Character.from_content(content)
        self.assertTrue(char.deaths)
        self.assertEqual(len(char.deaths), 19)

    def testDeathTypes(self):
        assisted_suicide = Death("Galarzaa", 280, killers=[Killer("Galarzaa", True), Killer("a pixy")],
                                 time=datetime.datetime.now())
        self.assertEqual(assisted_suicide.killer, assisted_suicide.killers[0])
        self.assertFalse(assisted_suicide.by_player)

        spawn_invasion = Death("Galarza", 270, killers=[Killer("a demon"), Killer("Nezune", True)])
        self.assertEqual(spawn_invasion.killer, spawn_invasion.killers[0])
        self.assertIsNone(spawn_invasion.killer.url)
        self.assertTrue(spawn_invasion.by_player)
        
    def testCharacterTibiaData(self):
        content = self._get_parsed_content(FILE_CHARACTER_TIBIADATA, False)
        char = Character.from_tibiadata(content)

        self.assertEqual(char.url_tibiadata, Character.get_url_tibiadata(char.name))
        self.assertIsInstance(char, Character)
        self.assertIsNotNone(char.guild_name)
        self.assertIsInstance(char.last_login, datetime.datetime)

        self.assertTrue(char.deaths[5].by_player)

    def testCharacterTibiaDataNotFound(self):
        content = self._get_parsed_content(FILE_CHARACTER_TIBIADATA_NOT_FOUND, False)
        char = Character.from_tibiadata(content)
        self.assertIsNone(char)

    def testCharacterTibiaDataInvalidJson(self):
        char = Character.from_tibiadata("<html><b>Not a json string</b></html>")
        self.assertIsNone(char)