import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.enums import Sex, Vocation
from tibiapy.models import Character
from tibiapy.parsers import CharacterParser
from tibiapy.urls import get_character_url
from tibiapy.utils import parse_tibia_datetime

FILE_CHARACTER_RESOURCE = "character/character.txt"
FILE_CHARACTER_NOT_FOUND = "character/characterNotFound.txt"
FILE_CHARACTER_FORMER_NAMES = "character/characterWithFormerNames.txt"
FILE_CHARACTER_FORMER_WORLD = "character/characterWithFormerWorld.txt"
FILE_CHARACTER_TRADED = "character/characterRecentlyTraded.txt"
FILE_CHARACTER_TRADED_KILLER = "character/character_with_traded_killer.txt"
FILE_CHARACTER_SPECIAL_POSITION = "character/characterWithSpecialPosition.txt"
FILE_CHARACTER_DELETION = "character/characterScheduledForDeletion.txt"
FILE_CHARACTER_DEATHS_COMPLEX = "character/characterWithComplexDeaths.txt"
FILE_CHARACTER_TITLE_BADGES = "character/characterWithTitleAndBadges.txt"
FILE_CHARACTER_NO_BADGES_SELECTED = "character/characterWithNoBadgesSelected.txt"
FILE_CHARACTER_MULTIPLE_HOUSES = "character/characterWithMultipleHouses.txt"
FILE_CHARACTER_TRUNCATED_DEATHS = "character/characterWithTruncatedDeaths.txt"


class TestCharacter(TestCommons):

    # region Tibia.com Character Tests
    def test_character_parser_from_content(self):
        """Testing parsing a character's HTML content"""
        character = CharacterParser.from_content(self.load_resource(FILE_CHARACTER_RESOURCE))
        self.assertEqual("Tschas", character.name)
        self.assertEqual("Gladera", character.world)
        self.assertEqual(Vocation.ELDER_DRUID, character.vocation)
        self.assertEqual(833, character.level)
        self.assertEqual(Sex.FEMALE, character.sex)
        self.assertIsNotNone(character.guild_membership)
        self.assertEqual("Bald Dwarfs", character.guild_membership.name)
        self.assertEqual("Exalted", character.guild_membership.rank)
        self.assertIsNotNone(character.guild_url)
        self.assertIsNone(character.married_to_url)
        self.assertEqual(character.guild_name, character.guild_membership.name)
        self.assertEqual(character.guild_rank, character.guild_membership.rank)
        self.assertTrue(character.is_premium)
        self.assertEqual(405, character.achievement_points)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(0, character.deaths.__len__())
        self.assertEqual(parse_tibia_datetime("Apr 16 2023, 00:43:29 CEST"), character.last_login)
        self.assertEqual(character.url, get_character_url(character.name))
        self.assertEqual(5, len(character.other_characters))
        self.assertFalse(character.is_hidden)
        self.assertIn(character.name, character.url)

    def test_character_parser_from_content_not_found(self):
        """Testing parsing a character not found page"""
        content = self.load_resource(FILE_CHARACTER_NOT_FOUND)
        char = CharacterParser.from_content(content)
        self.assertIsNone(char)

    def test_character_parser_from_content_traded(self):
        """Testing parsing a character that was traded recently"""
        content = self.load_resource(FILE_CHARACTER_TRADED)

        char = CharacterParser.from_content(content)

        self.assertIsInstance(char, Character)
        self.assertTrue(char.is_traded)
        self.assertTrue(any(c.is_traded for c in char.other_characters), "at least one character should be traded")

    def test_character_parser_from_content_with_former_names(self):
        """Testing parsing a character that has former names"""
        content = self.load_resource(FILE_CHARACTER_FORMER_NAMES)

        char = CharacterParser.from_content(content)

        self.assertIsNotEmpty(char.former_names)

    def test_character_parser_from_content_with_former_world(self):
        """Testing parsing a character that has a former world."""
        content = self.load_resource(FILE_CHARACTER_FORMER_NAMES)

        char = CharacterParser.from_content(content)

        self.assertIsNotNone(char.former_world)

    def test_character_parser_from_content_with_position(self):
        """Testing parsing a character with a position"""
        content = self.load_resource(FILE_CHARACTER_SPECIAL_POSITION)

        position = "CipSoft Member"

        char = CharacterParser.from_content(content)
        self.assertEqual(position, char.position)
        self.assertEqual(position, char.account_information.position)
        self.assertTrue(any(c.position == position for c in char.other_characters),
                        "at least one character should have a position")

    def test_character_parser_from_content_deleted_character(self):
        """Testing parsing a character scheduled for deletion"""
        content = self.load_resource(FILE_CHARACTER_DELETION)
        char = CharacterParser.from_content(content)
        self.assertEqual("Gutek Handless", char.name)
        self.assertIsNotNone(char.deletion_date)
        self.assertIsInstance(char.deletion_date, datetime.datetime)
        self.assertTrue(char.is_scheduled_for_deletion)

    def test_character_parser_from_content_complex_deaths(self):
        """Testing parsing a character with complex deaths (summons, assists, etc)"""
        content = self.load_resource(FILE_CHARACTER_DEATHS_COMPLEX)

        char = CharacterParser.from_content(content)

        deaths = char.deaths
        self.assertEqual(5, len(char.deaths))
        self.assertTrue(deaths[0].is_by_player)
        self.assertEqual(23, len(deaths[0].killers))
        self.assertTrue(deaths[0].killer.is_player)
        self.assertEqual(1, len(deaths[0].assists))

        self.assertEqual(1, len(deaths[1].killers))
        self.assertEqual(0, len(deaths[1].assists))

        self.assertEqual(11, len(deaths[2].killers))
        self.assertEqual(0, len(deaths[2].assists))
        self.assertEqual("a paladin familiar", deaths[2].killers[-1].summon)
        self.assertEqual("Alloy Hat", deaths[2].killers[-1].name)
        self.assertTrue(deaths[2].killers[-1].is_traded)

        self.assertEqual(12, len(deaths[3].killers))
        self.assertEqual(0, len(deaths[3].assists))
        self.assertEqual("Cliff Lee Burton", deaths[3].killers[-1].name)
        self.assertTrue(deaths[3].killers[-1].is_traded)

    def test_character_parser_from_content_badges_and_title(self):
        """Testing parsing a character with account badges and a title"""
        content = self.load_resource(FILE_CHARACTER_TITLE_BADGES)
        char = CharacterParser.from_content(content)
        self.assertEqual("Gold Hoarder", char.title)
        self.assertEqual(13, char.unlocked_titles)
        self.assertSizeEquals(char.account_badges, 8)

    def test_character_parser_from_content_no_selected_badges(self):
        """Testing parsing a character with visible badges but none selected."""
        content = self.load_resource(FILE_CHARACTER_NO_BADGES_SELECTED)
        char = CharacterParser.from_content(content)
        self.assertIsEmpty(char.account_badges)

    def test_character_parser_from_content_multiple_houses(self):
        """Testing parsing a character with multiple houses."""
        content = self.load_resource(FILE_CHARACTER_MULTIPLE_HOUSES)

        char = CharacterParser.from_content(content)

        self.assertSizeAtLeast(char.houses, 2)

    def test_character_parser_from_content_truncated_deaths(self):
        """Testing parsing a character with truncated daths"""
        content = self.load_resource(FILE_CHARACTER_TRUNCATED_DEATHS)
        char = CharacterParser.from_content(content)
        self.assertIsNotEmpty(char.deaths)
        self.assertTrue(char.deaths_truncated)

    def test_character_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            CharacterParser.from_content(content)

    # endregion
