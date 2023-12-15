import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.builders import GuildBuilder
from tibiapy.models import Guild, GuildHouse, GuildWars
from tibiapy.parsers import GuildParser, GuildWarsParser, GuildsSectionParser
from tibiapy.urls import get_guild_url, get_guild_wars_url, get_world_guilds_url

FILE_GUILD_FULL = "guild/guild.txt"
FILE_GUILD_NOT_FOUND = "guild/guildNotFound.txt"
FILE_GUILD_INFO_MINIMUM = "guild/guildMinimumInfo.txt"
FILE_GUILD_INFO_DISBANDING = "guild/guildDisbanding.txt"
FILE_GUILD_INFO_FORMATION = "guild/guildFormation.txt"
FILE_GUILD_LIST = "guildsSection/guildsSection.txt"
FILE_GUILD_LIST_NOT_FOUND = "guildsSection/guildsSectionNotFound.txt"
FILE_GUILD_IN_WAR = "guild/guildAtWar.txt"

FILE_GUILD_WAR_ACTIVE_HISTORY = "guildWars/guildWarActiveAndHistory.txt"
FILE_GUILD_WAR_EMPTY = "guildWars/guildWarEmpty.txt"
FILE_GUILD_WAR_UNACTIVE_HISTORY = "guildWars/guildWarUnactiveAndHistory.txt"


class TestsGuild(TestCommons):
    def setUp(self):
        self.guild = GuildBuilder()

    def test_guild_parser_from_content(self):
        """Testing parsing a guild"""
        content = self.load_resource(FILE_GUILD_FULL)

        guild = GuildParser.from_content(content)

        self.assertIsInstance(guild, Guild)
        self.assertEqual("Bald Dwarfs", guild.name)
        self.assertEqual(guild.url, get_guild_url(guild.name))
        self.assertEqual(guild.url_wars, get_guild_wars_url(guild.name))
        self.assertTrue(guild.active)
        self.assertIsInstance(guild.founded, datetime.date)
        self.assertTrue(guild.open_applications)
        self.assertIsNotNone(guild.description)
        self.assertIsNotNone(guild.homepage)
        self.assertTrue(guild.members)
        self.assertEqual(guild.member_count, len(guild.members))
        self.assertIsInstance(guild.online_members, list)
        self.assertEqual(len(guild.online_members), guild.online_count)
        self.assertTrue(guild.ranks)
        for member in guild.members:
            self.assertIsInstance(member.level, int)
            self.assertIsInstance(member.joined_on, datetime.date)
        for invited in guild.invites:
            self.assertIsNotNone(invited.name)
            self.assertIsInstance(invited.invited_on, datetime.date)

        self.assertEqual("Krisph", guild.leader.name)
        self.assertEqual(10, len(guild.vice_leaders))

        self.assertEqual(11, len(guild.members_by_rank['Emperor']))

        self.assertIsInstance(guild.guildhall, GuildHouse)
        self.assertIsInstance(guild.guildhall.paid_until, datetime.date)

    def test_guild_parser_from_content_not_found(self):
        """Testing parsing a non existent guild"""
        content = self.load_resource(FILE_GUILD_NOT_FOUND)
        guild = GuildParser.from_content(content)
        self.assertIsNone(guild)

    def test_guild_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibiacom section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            GuildParser.from_content(content)


    def test_guild_parser_from_content_minimum_info(self):
        """Testing parsing a guild with the minimum information possible"""
        content = self.load_resource(FILE_GUILD_INFO_MINIMUM)

        guild = GuildParser.from_content(content)

        self.assertIsNone(guild.disband_condition)
        self.assertIsNone(guild.disband_date)
        self.assertIsNone(guild.guildhall)
        self.assertIsNone(guild.homepage)
        self.assertIsNone(guild.description,)
        self.assertEqual("Gentebra", guild.world)
        self.assertEqual(datetime.date(year=2022, month=3, day=23), guild.founded)

    def test_guild_parser_from_content_in_war(self):
        content = self.load_resource(FILE_GUILD_IN_WAR)
        guild = GuildParser.from_content(content)

        self.assertIsInstance(guild, Guild)
        self.assertFalse(guild.open_applications)
        self.assertTrue(guild.active_war)

    def test_guild_parser_from_content_disbanding(self):
        """Testing parsing a guild that is disbanding"""
        content = self.load_resource(FILE_GUILD_INFO_DISBANDING)

        guild = GuildParser.from_content(content)

        self.assertIsNone(guild.description)
        self.assertTrue(guild.active)
        self.assertTrue(guild.open_applications)
        self.assertIsNotNone(guild.disband_condition)
        self.assertEqual(datetime.date(2023,5,30), guild.disband_date)

    def test_guild_parser_from_content_formation(self):
        """Testing parsing a guild that is in formation"""
        content = self.load_resource(FILE_GUILD_INFO_FORMATION)

        guild = GuildParser.from_content(content)

        self.assertFalse(guild.active)
        self.assertIsNotNone(guild.disband_condition)
        self.assertEqual(datetime.date(2023, 5, 20), guild.disband_date)

    def test_guilds_section_parser_from_content(self):
        """Testing parsing the list of guilds of a world"""
        content = self.load_resource(FILE_GUILD_LIST)

        guilds_section = GuildsSectionParser.from_content(content)
        guilds = guilds_section.entries

        self.assertEqual(6, len(guilds_section.active_guilds))
        self.assertEqual(5, len(guilds_section.in_formation_guilds))
        self.assertEqual(90, len(guilds_section.available_worlds))
        self.assertEqual(get_world_guilds_url(guilds_section.world), guilds_section.url)
        self.assertEqual("Gravitera", guilds[0].world)
        self.assertTrue(guilds[0].active)
        self.assertFalse(guilds[-1].active)

    def test_guilds_section_parser_from_content_not_found(self):
        """Testing parsing the guild list of a world that doesn't exist"""
        content = self.load_resource(FILE_GUILD_LIST_NOT_FOUND)
        guilds_section = GuildsSectionParser.from_content(content)
        self.assertIsNotNone(guilds_section)
        self.assertIsNone(guilds_section.world)
        self.assertEqual(0, len(guilds_section.entries))

    def test_guilds_section_parser_from_content_unrelated(self):
        """Testing parsing and unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            GuildsSectionParser.from_content(content)


    # region Guild War Tests
    def test_guild_wars_parser_from_content_active_history(self):
        """Testing parsing the guild wars of a guild currently in war and with war history."""
        content = self.load_resource(FILE_GUILD_WAR_ACTIVE_HISTORY)
        guild_wars = GuildWarsParser.from_content(content)

        self.assertIsInstance(guild_wars, GuildWars)
        self.assertEqual("Realm Honor", guild_wars.name)
        self.assertIsNotNone(guild_wars.is_current)
        self.assertEqual(guild_wars.name, guild_wars.is_current.guild_name)
        self.assertEqual(0, guild_wars.is_current.guild_score)
        self.assertEqual("Nights Watch", guild_wars.is_current.opponent_name)
        self.assertEqual(0, guild_wars.is_current.opponent_score)
        self.assertEqual(1000, guild_wars.is_current.score_limit)

        self.assertEqual(15, len(guild_wars.history))

        self.assertEqual(guild_wars.name, guild_wars.history[0].guild_name)
        self.assertEqual(0, guild_wars.history[0].guild_score)
        self.assertEqual(None, guild_wars.history[0].opponent_name)
        self.assertEqual(0, guild_wars.history[0].opponent_score)
        self.assertEqual(1000, guild_wars.history[0].score_limit)
        self.assertTrue(guild_wars.history[0].surrender)

        self.assertEqual(guild_wars.name, guild_wars.history[1].guild_name)
        self.assertEqual(0, guild_wars.history[1].guild_score)
        self.assertEqual(None, guild_wars.history[1].opponent_name)
        self.assertEqual(0, guild_wars.history[1].opponent_score)
        self.assertEqual(1000, guild_wars.history[1].score_limit)
        self.assertEqual(guild_wars.name, guild_wars.history[1].winner)

    def test_guild_wars_parser_from_content_empty(self):
        """Testing parsing the guild wars of a guild that has never been in a war"""
        content = self.load_resource(FILE_GUILD_WAR_EMPTY)
        guild_wars = GuildWarsParser.from_content(content)

        self.assertEqual("Alliance Of Friends", guild_wars.name)
        self.assertIsNone(guild_wars.is_current)
        self.assertFalse(guild_wars.history)

    def test_guild_wars_parser_from_content_unactive_history(self):
        """Testing parsing the guild wars of a war currently not in war and with war history."""
        content = self.load_resource(FILE_GUILD_WAR_UNACTIVE_HISTORY)
        guild_wars = GuildWarsParser.from_content(content)

        self.assertIsInstance(guild_wars, GuildWars)
        self.assertEqual("Bald Dwarfs", guild_wars.name)
        self.assertIsNone(guild_wars.is_current)

        self.assertEqual(2, len(guild_wars.history))

        self.assertEqual(guild_wars.name, guild_wars.history[0].guild_name)
        self.assertEqual(0, guild_wars.history[0].guild_score)
        self.assertEqual(None, guild_wars.history[0].opponent_name)
        self.assertEqual(0, guild_wars.history[0].opponent_score)
        self.assertEqual(100, guild_wars.history[0].score_limit)
        self.assertTrue(guild_wars.history[0].surrender)

    # endregion
