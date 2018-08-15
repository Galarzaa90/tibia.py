from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Character
from tibiapy.utils import parse_tibia_datetime

PATH_CHARACTER_RESOURCE = "character.txt"


class TestCharacter(TestTibiaPy):

    def testGuilds(self):
        character = Character.from_content(self._get_parsed_content(PATH_CHARACTER_RESOURCE, False))
        self._compare_character(Character("Tschas", "Gladera", "Druid", 205, "female"), character)
        self.assertIsNotNone(character.guild_membership)
        self.assertEqual("Redd Alliance", character.guild_membership["guild"])
        self.assertEqual("Mentor", character.guild_membership["rank"])
        self.assertEqual("Free Account", character.account_status)
        self.assertEqual(139, character.achievement_points)
        self.assertIsNone(character.house)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(0, character.deaths.__len__())
        self.assertEqual(parse_tibia_datetime("Apr 22 2018, 16:00:38 CEST"), character.last_login)

    def _compare_character(self, mock_character, character):
        self.assertEqual(mock_character.name, character.name)
        self.assertEqual(mock_character.world, character.world)
        self.assertEqual(mock_character.vocation, character.vocation)
        self.assertEqual(mock_character.level, character.level)
        self.assertEqual(mock_character.sex, character.sex)
