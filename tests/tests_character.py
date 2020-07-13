import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import AccountBadge, Character, CharacterHouse, Death, InvalidContent, Killer
from tibiapy.enums import AccountStatus, Sex, Vocation
from tibiapy.utils import parse_tibia_datetime

FILE_CHARACTER_RESOURCE = "character/tibiacom_full.txt"
FILE_CHARACTER_NOT_FOUND = "character/tibiacom_not_found.txt"
FILE_CHARACTER_FORMER_NAMES = "character/tibiacom_former_names.txt"
FILE_CHARACTER_SPECIAL_POSITION = "character/tibiacom_special_position.txt"
FILE_CHARACTER_DELETION = "character/tibiacom_deletion.txt"
FILE_CHARACTER_DEATHS_COMPLEX = "character/tibiacom_deaths_complex.txt"
FILE_CHARACTER_TITLE_BADGES = "character/tibiacom_title_badges.txt"
FILE_CHARACTER_NO_BADGES_SELECTED = "character/tibiacom_no_badges_selected.txt"
FILE_CHARACTER_MULTIPLE_HOUSES = "character/tibiacom_multiple_houses.txt"
FILE_CHARACTER_TRUNCATED_DEATHS = "character/tibiacom_truncated_deaths.txt"


class TestCharacter(TestCommons, unittest.TestCase):
    def _compare_character(self, mock_character, character):
        self.assertEqual(mock_character.name, character.name)
        self.assertEqual(mock_character.world, character.world)
        self.assertEqual(mock_character.vocation, character.vocation)
        self.assertEqual(mock_character.level, character.level)
        self.assertEqual(mock_character.sex, character.sex)

    # region Tibia.com Character Tests
    def test_character_from_content(self):
        """Testing parsing a character's HTML content"""
        character = Character.from_content(self.load_resource(FILE_CHARACTER_RESOURCE))
        self._compare_character(Character("Tschas", "Gladera", Vocation.DRUID, 260, Sex.FEMALE), character)
        self.assertIsNotNone(character.guild_membership)
        self.assertEqual("Atlantis", character.guild_membership.name)
        self.assertEqual("Gaia", character.guild_membership.rank)
        self.assertIsNotNone(character.guild_url)
        self.assertIsNone(character.married_to_url)
        self.assertEqual(character.guild_name, character.guild_membership.name)
        self.assertEqual(character.guild_rank, character.guild_membership.rank)
        self.assertEqual(AccountStatus.FREE_ACCOUNT, character.account_status)
        self.assertEqual(182, character.achievement_points)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(0, character.deaths.__len__())
        self.assertEqual(parse_tibia_datetime("Aug 04 2019, 13:56:59 CEST"), character.last_login)
        self.assertEqual(character.url, Character.get_url(character.name))
        self.assertEqual(5, len(character.other_characters))
        self.assertFalse(character.hidden)

    def test_character_from_content_not_found(self):
        """Testing parsing a character not found page"""
        content = self.load_resource(FILE_CHARACTER_NOT_FOUND)
        char = Character.from_content(content)
        self.assertIsNone(char)

    def test_character_from_content_with_former_names(self):
        """Testing parsing a character that has former names"""
        content = self.load_resource(FILE_CHARACTER_FORMER_NAMES)
        char = Character.from_content(content)
        self.assertIsInstance(char.former_names, list)
        self.assertTrue(char.former_names)
        self.assertEqual(len(char.former_names), 2)

        self.assertIsInstance(char.houses[0], CharacterHouse)
        self.assertEqual(char.houses[0].owner, char.name)
        self.assertEqual(char.houses[0].town, "Darashia")
        self.assertEqual(char.houses[0].world, char.world)
        self.assertIsInstance(char.houses[0].paid_until_date, datetime.date)

    def test_character_from_content_with_position(self):
        """Testing parsing a character with a position"""
        content = self.load_resource(FILE_CHARACTER_SPECIAL_POSITION)

        position = "CipSoft Member"

        char = Character.from_content(content)
        self.assertEqual("Steve", char.name)
        self.assertEqual(position, char.position)
        self.assertEqual(position, char.account_information.position)
        steve_other = char.other_characters[2]
        self.assertEqual("Steve", steve_other.name)
        self.assertEqual("CipSoft Member", steve_other.position)

    def test_character_from_content_deleted_character(self):
        """Testing parsing a character scheduled for deletion"""
        content = self.load_resource(FILE_CHARACTER_DELETION)
        char = Character.from_content(content)
        self.assertEqual("Expendable Dummy", char.name)
        self.assertIsNotNone(char.deletion_date)
        self.assertIsInstance(char.deletion_date, datetime.datetime)
        self.assertEqual(parse_tibia_datetime("Oct 08 2018 22:17:00 CEST"), char.deletion_date)

    def test_character_from_content_complex_deaths(self):
        """Testing parsing a character with complex deaths (summons, assists, etc)"""
        content = self.load_resource(FILE_CHARACTER_DEATHS_COMPLEX)
        char = Character.from_content(content)
        self.assertTrue(char.deaths)
        self.assertIsInstance(char.deaths[0], Death)
        self.assertEqual(len(char.deaths), 19)
        oldest_death = char.deaths[-1]
        self.assertEqual(oldest_death.killer.summon, "a fire elemental")

    def test_character_from_content_badges_and_title(self):
        """Testing parsing a character with account badges and a title"""
        content = self.load_resource(FILE_CHARACTER_TITLE_BADGES)
        char = Character.from_content(content)
        self.assertEqual("Galarzaa Fidera", char.name)
        self.assertEqual(406, char.achievement_points)
        self.assertEqual("Gold Hoarder", char.title)
        self.assertEqual(8, char.unlocked_titles)
        self.assertEqual(6, len(char.account_badges))
        for badge in char.account_badges:
            self.assertIsInstance(badge, AccountBadge)
            self.assertIsInstance(badge.name, str)
            self.assertIsInstance(badge.icon_url, str)
            self.assertIsInstance(badge.description, str)

    def test_character_from_content_no_selected_badges(self):
        """Testing parsing a character with visible badges but none selected."""
        content = self.load_resource(FILE_CHARACTER_NO_BADGES_SELECTED)
        char = Character.from_content(content)
        self.assertEqual("Cozzackirycerz", char.name)
        self.assertEqual(25, char.achievement_points)
        self.assertIsNone(char.title)
        self.assertEqual(3, char.unlocked_titles)
        self.assertEqual(0, len(char.account_badges))
        self.assertEqual(0, len(char.former_names))

    def test_character_from_content_multiple_houses(self):
        """Testing parsing a character with multiple houses."""
        content = self.load_resource(FILE_CHARACTER_MULTIPLE_HOUSES)
        char = Character.from_content(content)
        self.assertEqual("Sayuri Nowan", char.name)
        self.assertEqual(2, len(char.houses))
        first_house = char.houses[0]
        second_house = char.houses[1]
        self.assertEqual("Cormaya 10", first_house.name)
        self.assertEqual("Old Heritage Estate", second_house.name)
        self.assertEqual("Edron", first_house.town)
        self.assertEqual("Rathleton", second_house.town)

    def test_character_from_content_truncated_deaths(self):
        """Testing parsing a character with truncated daths"""
        content = self.load_resource(FILE_CHARACTER_TRUNCATED_DEATHS)
        char = Character.from_content(content)
        self.assertEqual("Godlike Terror", char.name)
        self.assertEqual(51, len(char.deaths))
        self.assertTrue(char.deaths_truncated)

    def test_character_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Character.from_content(content)

    # endregion

    def test_death_types(self):
        """Testing different death types"""
        assisted_suicide = Death("Galarzaa", 280, killers=[Killer("Galarzaa", True), Killer("a pixy")],
                                 time=datetime.datetime.now())
        self.assertEqual(assisted_suicide.killer, assisted_suicide.killers[0])
        self.assertFalse(assisted_suicide.by_player)

        spawn_invasion = Death("Galarza", 270, killers=[Killer("a demon"), Killer("Nezune", True)])
        self.assertEqual(spawn_invasion.killer, spawn_invasion.killers[0])
        self.assertIsNone(spawn_invasion.killer.url)
        self.assertTrue(spawn_invasion.by_player)
