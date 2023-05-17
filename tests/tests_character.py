import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent
from tibiapy.models import Death, DeathParticipant, AccountBadge, CharacterHouse, Character
from tibiapy.parsers.character import CharacterParser
from tibiapy.urls import get_character_url
from tibiapy.utils import parse_tibia_datetime

FILE_CHARACTER_RESOURCE = "character/character.txt"
FILE_CHARACTER_NOT_FOUND = "character/characterNotFound.txt"
FILE_CHARACTER_FORMER_NAMES = "character/characterFormerNames.txt"
FILE_CHARACTER_TRADED = "character/characterTraded.txt"
FILE_CHARACTER_TRADED_KILLER = "character/character_with_traded_killer.txt"
FILE_CHARACTER_SPECIAL_POSITION = "character/characterSpecialPosition.txt"
FILE_CHARACTER_DELETION = "character/characterDeletionScheduled.txt"
FILE_CHARACTER_DEATHS_COMPLEX = "character/characterWithComplexDeaths.txt"
FILE_CHARACTER_TITLE_BADGES = "character/characterWithTitleAndBadges.txt"
FILE_CHARACTER_NO_BADGES_SELECTED = "character/characterNoBadgesSelected.txt"
FILE_CHARACTER_MULTIPLE_HOUSES = "character/characterMultipleHouses.txt"
FILE_CHARACTER_TRUNCATED_DEATHS = "character/characterTruncatedDeaths.txt"


class TestCharacter(TestCommons, unittest.TestCase):
    def _compare_character(self, mock_character, character):
        self.assertEqual(mock_character.name, character.name)
        self.assertEqual(mock_character.world, character.world)
        self.assertEqual(mock_character.vocation, character.vocation)
        self.assertEqual(mock_character.level, character.level)
        self.assertEqual(mock_character.sex, character.sex)

    # region Tibia.com Character Tests
    def test_character_parser_from_content(self):
        """Testing parsing a character's HTML content"""
        character = CharacterParser.from_content(self.load_resource(FILE_CHARACTER_RESOURCE))
        # TODO: Reenable
        # self._compare_character(Character("Tschas", "Gladera", Vocation.ELDER_DRUID, 522, Sex.FEMALE), character)
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
        self.assertFalse(character.hidden)

        # Badges
        self.assertEqual(8, len(character.account_badges))
        badge = character.account_badges[0]
        self.assertEqual("Ancient Hero", badge.name)
        self.assertEqual("The account is older than 15 years.", badge.description)

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
        self.assertEqual("King Dragotz", char.name)
        self.assertTrue(char.traded)
        char_in_other = char.other_characters[0]
        self.assertEqual("King Dragotz", char_in_other.name)
        self.assertTrue(char_in_other.traded)

    def test_character_parser_from_content_with_former_names(self):
        """Testing parsing a character that has former names"""
        content = self.load_resource(FILE_CHARACTER_FORMER_NAMES)

        char = CharacterParser.from_content(content)

        self.assertIsInstance(char.former_names, list)
        self.assertTrue(char.former_names)
        self.assertEqual(len(char.former_names), 3)

    def test_character_parser_from_content_with_position(self):
        """Testing parsing a character with a position"""
        content = self.load_resource(FILE_CHARACTER_SPECIAL_POSITION)

        position = "CipSoft Member"

        char = CharacterParser.from_content(content)
        self.assertEqual("Steve", char.name)
        self.assertEqual(position, char.position)
        self.assertEqual(position, char.account_information.position)
        steve_other = char.other_characters[2]
        self.assertEqual("Steve", steve_other.name)
        self.assertEqual("CipSoft Member", steve_other.position)

    def test_character_parser_from_content_deleted_character(self):
        """Testing parsing a character scheduled for deletion"""
        content = self.load_resource(FILE_CHARACTER_DELETION)
        char = CharacterParser.from_content(content)
        self.assertEqual("Gutek Handless", char.name)
        self.assertIsNotNone(char.deletion_date)
        self.assertIsInstance(char.deletion_date, datetime.datetime)
        self.assertEqual(datetime.datetime(2023, 7, 4, 16, 10, 41, tzinfo=datetime.timezone.utc), char.deletion_date)

    def test_character_parser_from_content_complex_deaths(self):
        """Testing parsing a character with complex deaths (summons, assists, etc)"""
        content = self.load_resource(FILE_CHARACTER_DEATHS_COMPLEX)
        char = CharacterParser.from_content(content)
        self.assertEqual(5, len(char.deaths))
        death1, death2, death3, death4, death5 = char.deaths
        self.assertIsInstance(death1, Death)
        self.assertEqual(23, len(death1.killers))
        self.assertEqual(1, len(death1.assists))

        self.assertIsInstance(death2, Death)
        self.assertEqual(1, len(death2.killers))
        self.assertEqual(0, len(death2.assists))

        self.assertIsInstance(death3, Death)
        self.assertEqual(11, len(death3.killers))
        self.assertEqual(0, len(death3.assists))
        self.assertEqual("a paladin familiar", death3.killers[-1].summon)
        self.assertEqual("Alloy Hat", death3.killers[-1].name)
        self.assertTrue(death3.killers[-1].traded)

        self.assertIsInstance(death4, Death)
        self.assertEqual(12, len(death4.killers))
        self.assertEqual(0, len(death4.assists))
        self.assertEqual("Cliff Lee Burton", death4.killers[-1].name)
        self.assertTrue(death4.killers[-1].traded)

    def test_character_parserparser_from_content_badges_and_title(self):
        """Testing parsing a character with account badges and a title"""
        content = self.load_resource(FILE_CHARACTER_TITLE_BADGES)
        char = CharacterParser.from_content(content)
        self.assertEqual("Galarzaa Fidera", char.name)
        self.assertEqual(410, char.achievement_points)
        self.assertEqual("Gold Hoarder", char.title)
        self.assertEqual(13, char.unlocked_titles)
        self.assertEqual(8, len(char.account_badges))
        for badge in char.account_badges:
            self.assertIsInstance(badge, AccountBadge)
            self.assertIsInstance(badge.name, str)
            self.assertIsInstance(badge.icon_url, str)
            self.assertIsInstance(badge.description, str)

    def test_character_parser_from_content_no_selected_badges(self):
        """Testing parsing a character with visible badges but none selected."""
        content = self.load_resource(FILE_CHARACTER_NO_BADGES_SELECTED)
        char = CharacterParser.from_content(content)
        self.assertEqual("Cozzackirycerz", char.name)
        self.assertEqual(25, char.achievement_points)
        self.assertIsNone(char.title)
        self.assertEqual(3, char.unlocked_titles)
        self.assertEqual(0, len(char.account_badges))
        self.assertEqual(0, len(char.former_names))

    def test_character_parser_from_content_multiple_houses(self):
        """Testing parsing a character with multiple houses."""
        content = self.load_resource(FILE_CHARACTER_MULTIPLE_HOUSES)

        char = CharacterParser.from_content(content)

        self.assertEqual(2, len(char.houses))
        first_house = char.houses[0]
        second_house = char.houses[1]
        self.assertEqual("Coastwood 8", first_house.name)
        self.assertEqual("Tunnel Gardens 5", second_house.name)
        self.assertEqual("Ab'Dendriel", first_house.town)
        self.assertEqual("Kazordoon", second_house.town)

    def test_character_parser_from_content_truncated_deaths(self):
        """Testing parsing a character with truncated daths"""
        content = self.load_resource(FILE_CHARACTER_TRUNCATED_DEATHS)
        char = CharacterParser.from_content(content)
        self.assertEqual("Godlike Terror", char.name)
        self.assertEqual(51, len(char.deaths))
        self.assertTrue(char.deaths_truncated)

    def test_character_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CharacterParser.from_content(content)

    # endregion

    def test_death_types(self):
        """Testing different death types"""
        assisted_suicide = Death(level=280,
                                 killers=[
                                     DeathParticipant(name="Galarzaa", player=True, summon=None, traded=False),
                                     DeathParticipant(name="a pixy", player=False, summon=None, traded=False)
                                 ],
                                 assists=[],
                                 time=datetime.datetime.now())
        self.assertEqual(assisted_suicide.killer, assisted_suicide.killers[0])
        self.assertTrue(assisted_suicide.by_player)

        spawn_invasion = Death(level=270,
                               killers=[
                                   DeathParticipant(name="a demon", player=False, summon=None, traded=False),
                                   DeathParticipant(name="Nezune", player=True, summon=None, traded=False)
                               ],
                               assists=[],
                               time=datetime.datetime.now())
        self.assertEqual(spawn_invasion.killer, spawn_invasion.killers[0])
        self.assertIsNone(spawn_invasion.killer.url)
        self.assertTrue(spawn_invasion.by_player)
