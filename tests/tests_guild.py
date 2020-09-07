import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import Guild, GuildHouse, GuildInvite, GuildMember, GuildWars, InvalidContent, ListedGuild

FILE_GUILD_FULL = "guild/tibiacom_full.txt"
FILE_GUILD_NOT_FOUND = "guild/tibiacom_not_found.txt"
FILE_GUILD_INFO_COMPLETE = "guild/tibiacom_info_complete.txt"
FILE_GUILD_INFO_MINIMUM = "guild/tibiacom_info_minimum.txt"
FILE_GUILD_INFO_DISBANDING = "guild/tibiacom_info_disbanding.txt"
FILE_GUILD_INFO_FORMATION = "guild/tibiacom_info_formation.txt"
FILE_GUILD_LIST = "guild/tibiacom_list.txt"
FILE_GUILD_LIST_NOT_FOUND = "guild/tibiacom_list_not_found.txt"
FILE_GUILD_IN_WAR = "guild/tibiacom_war.txt"

FILE_GUILD_WAR_ACTIVE_HISTORY = "guild/wars/tibiacom_active_history.txt"
FILE_GUILD_WAR_EMPTY = "guild/wars/tibiacom_empty.txt"
FILE_GUILD_WAR_UNACTIVE_HISTORY = "guild/wars/tibiacom_unactive_history.txt"


class TestsGuild(TestCommons, unittest.TestCase):
    def setUp(self):
        self.guild = Guild()

    def test_guild_from_content(self):
        """Testing parsing a guild"""
        content = self.load_resource(FILE_GUILD_FULL)
        guild = Guild.from_content(content)
        self.assertIsInstance(guild, Guild, "Guild should be a Guild object.")
        self.assertEqual(guild.url, Guild.get_url(guild.name))
        self.assertEqual(guild.url_wars, Guild.get_url_wars(guild.name))
        self.assertTrue(guild.active, "Guild should be active")
        self.assertIsInstance(guild.founded, datetime.date, "Guild founded date should be an instance of datetime.date")
        self.assertTrue(guild.open_applications, "Guild applications should be open")
        self.assertIsNotNone(guild.description, "Guild should have a description")
        self.assertTrue(guild.members, "Guild should have members")
        self.assertEqual(guild.member_count, len(guild.members))
        self.assertTrue(guild.invites, "Guild should have invites")
        self.assertIsInstance(guild.online_members, list, "Guild online members should be a list.")
        self.assertEqual(len(guild.online_members), guild.online_count, "Length of online_members should be equal "
                                                                        "to online_count")
        self.assertTrue(guild.ranks, "Guild ranks should not be empty.")
        for member in guild.members:
            self.assertIsInstance(member.level, int, "Member level should be an integer.")
            self.assertIsInstance(member.joined, datetime.date, "Member's joined date should be datetime.date.")
        for invited in guild.invites:
            self.assertIsNotNone(invited.name, "Invited character's name should not be None.")
            self.assertIsInstance(invited.date, datetime.date, "Invited character's date should be datetime.date.")

        self.assertEqual(8, len(guild.members_by_rank['Vice Leader']))

        self.assertIsInstance(guild.guildhall, GuildHouse)
        self.assertEqual(guild.guildhall.owner, guild.members[0].name)
        self.assertEqual(guild.guildhall.world, guild.world)
        self.assertIsInstance(guild.guildhall.paid_until_date, datetime.date)

    def test_guild_from_content_not_found(self):
        """Testing parsing a non existent guild"""
        content = self.load_resource(FILE_GUILD_NOT_FOUND)
        guild = Guild.from_content(content)
        self.assertIsNone(guild)

    def test_guild_from_content_unrelated(self):
        """Testing parsing an unrelated tibiacom section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Guild.from_content(content)

    def test_guild_from_content_complete_info(self):
        """Testing parsing a guild with all information possible"""
        content = self.load_parsed_resource(FILE_GUILD_INFO_COMPLETE)
        self.guild._parse_guild_disband_info(content)
        self.assertIsNone(self.guild.disband_condition, "Guild should not be under disband warning")
        self.assertIsNone(self.guild.disband_date, "Guild should not have disband date")

        self.guild._parse_guild_guildhall(content)
        self.assertIsNotNone(self.guild.guildhall, "Guild should have guildhall")
        self.assertEqual(self.guild.guildhall.name, "Sky Lane, Guild 1")
        self.assertEqual(self.guild.guildhall.paid_until_date, datetime.date(2018, 8, 26))

        self.guild._parse_guild_homepage(content)
        self.assertIsNotNone(self.guild.homepage, "Guild homepage must exist")
        self.assertEqual("tibiammo.reddit.com", self.guild.homepage)

        self.guild._parse_application_info(content)
        self.assertTrue(self.guild.open_applications, "Guild should be open to applications")

        self.guild._parse_guild_info(content)
        self.assertIsNotNone(self.guild.description, "Guild description must exist")
        self.assertEqual("Gladera", self.guild.world)
        self.assertEqual(datetime.date(2015, 7, 23), self.guild.founded)
        self.assertTrue(self.guild.active, "Guild should be active")

    def test_guild_from_content_minimum_info(self):
        """Testing parsing a guild with the minimum information possible"""
        content = self.load_parsed_resource(FILE_GUILD_INFO_MINIMUM)
        self.guild._parse_guild_disband_info(content)
        self.assertIsNone(self.guild.disband_condition, "Guild should not be under disband warning")
        self.assertIsNone(self.guild.disband_date, "Guild should not have disband date")

        self.guild._parse_guild_guildhall(content)
        self.assertIsNone(self.guild.guildhall, "Guild should not have a guildhall")

        self.guild._parse_guild_homepage(content)
        self.assertIsNone(self.guild.homepage, "Guild should not have a guildhall")

        self.guild._parse_guild_info(content)
        self.assertIsNone(self.guild.description, "Guild description must not exist")
        self.assertEqual("Gladera", self.guild.world)
        self.assertEqual(datetime.date(year=2018, month=5, day=18), self.guild.founded)

    def test_guild_from_content_in_war(self):
        content = self.load_resource(FILE_GUILD_IN_WAR)
        guild = Guild.from_content(content)

        self.assertIsInstance(guild, Guild)
        self.assertFalse(guild.open_applications)
        self.assertTrue(guild.active_war)

    def test_guild_from_content_disbanding(self):
        """Testing parsing a guild that is disbanding"""
        content = self.load_parsed_resource(FILE_GUILD_INFO_DISBANDING)
        self.guild._parse_guild_info(content)
        self.assertTrue(self.guild.active, "Guild should be active")

        self.guild._parse_guild_disband_info(content)
        self.assertIsNotNone(self.guild.disband_condition, "Guild should have a disband warning")
        self.assertEqual(self.guild.disband_date, datetime.date(2018, 8, 17), "Guild should have disband date")

    def test_guild_from_content_formation(self):
        """Testing parsing a guild that is in formation"""
        content = self.load_parsed_resource(FILE_GUILD_INFO_FORMATION)
        Guild._parse_guild_info(self.guild, content)
        self.assertFalse(self.guild["active"], "Guild should not be active")

        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNotNone(self.guild.disband_condition, "Guild should have a disband warning")
        self.assertEqual(self.guild.disband_date, datetime.date(2018, 8, 16), "Guild should have disband date")

    def test_listed_guild_from_content(self):
        """Testing parsing the list of guilds of a world"""
        content = self.load_resource(FILE_GUILD_LIST)
        guilds = ListedGuild.list_from_content(content)
        self.assertTrue(guilds)
        self.assertIsNotNone(ListedGuild.get_world_list_url(guilds[0].world))
        self.assertEqual("Zuna", guilds[0].world)
        self.assertTrue(guilds[0].active)
        self.assertFalse(guilds[-1].active)

    def test_listed_guild_from_content_not_found(self):
        """Testing parsing the guild list of a world that doesn't exist"""
        content = self.load_resource(FILE_GUILD_LIST_NOT_FOUND)
        guilds = ListedGuild.list_from_content(content)
        self.assertIsNone(guilds)

    def test_listed_guild_from_content_unrelated(self):
        """Testing parsing and unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            ListedGuild.list_from_content(content)

    def test_parse_invited_member_date(self):
        """Testing the invitation date of a invited member"""
        name = "Tschas"
        date = "Invitation Date"
        values = name, date
        self.guild._parse_invited_member(values)
        self.assertIsNotNone(self.guild.invites)
        self.assertListEqual(self.guild.invites, [])

    def test_parse_invited_member(self):
        """Testing parsing an invited member"""
        name = "Tschas"
        date = "Jun 20 2018"
        values = name, date
        Guild._parse_invited_member(self.guild, values)
        self.assertIsNotNone(self.guild.invites)
        self.assertIsNotNone(self.guild.invites[0])
        self.assertEqual(self.guild.invites[0].name, name)
        self.assertEqual(self.guild.invites[0].date, datetime.date(2018, 6, 20))

    def test_guild_member_init_join_date(self):
        """Testing different combinations of join dates for instance creation"""
        self.assertIsInstance(GuildMember(joined="Jul 20 2018").joined, datetime.date)
        self.assertIsInstance(GuildMember(joined=datetime.date.today()).joined, datetime.date)
        self.assertIsInstance(GuildMember(joined=datetime.datetime.now()).joined, datetime.date)
        self.assertIsNone(GuildMember(joined=None).joined)
        self.assertIsNone(GuildMember(joined="Jul 20").joined)

    def test_guild_invite_init_invite_date(self):
        """Testing different combinations of invite dates for instance creation"""
        self.assertIsInstance(GuildInvite(date="Jul 20 2018").date, datetime.date)
        self.assertIsInstance(GuildInvite(date=datetime.date.today()).date, datetime.date)
        self.assertIsInstance(GuildInvite(date=datetime.datetime.now()).date, datetime.date)
        self.assertIsNone(GuildInvite(date=None).date)
        self.assertIsNone(GuildInvite(date="Jul 20").date)

    def test_guild_init_founded(self):
        """Testing different founded date inputs for instance creation"""
        self.assertIsInstance(Guild(founded="Jul 20 2018").founded, datetime.date)
        self.assertIsInstance(Guild(founded=datetime.date.today()).founded, datetime.date)
        self.assertIsInstance(Guild(founded=datetime.datetime.now()).founded, datetime.date)
        self.assertIsNone(Guild(founded=None).founded)
        self.assertIsNone(Guild(founded="Jul 20").founded)

    # region Guild War Tests
    def test_guild_wars_from_content_active_history(self):
        """Testing parsing the guild wars of a guild currently in war and with war history."""
        content = self.load_resource(FILE_GUILD_WAR_ACTIVE_HISTORY)
        guild_wars = GuildWars.from_content(content)

        self.assertIsInstance(guild_wars, GuildWars)
        self.assertEqual("Army Geddon", guild_wars.name)
        self.assertIsNotNone(guild_wars.current)
        self.assertEqual(guild_wars.name, guild_wars.current.guild_name)
        self.assertEqual(178, guild_wars.current.guild_score)
        self.assertEqual("Willyboiis Boys", guild_wars.current.opponent_name)
        self.assertEqual(218, guild_wars.current.opponent_score)
        self.assertEqual(1000, guild_wars.current.score_limit)

        self.assertEqual(2, len(guild_wars.history))

        self.assertEqual(guild_wars.name, guild_wars.history[0].guild_name)
        self.assertEqual(0, guild_wars.history[0].guild_score)
        self.assertEqual(None, guild_wars.history[0].opponent_name)
        self.assertEqual(0, guild_wars.history[0].opponent_score)
        self.assertEqual(420, guild_wars.history[0].score_limit)
        self.assertTrue(guild_wars.history[0].surrender)

        self.assertEqual(guild_wars.name, guild_wars.history[1].guild_name)
        self.assertEqual(500, guild_wars.history[1].guild_score)
        self.assertEqual(None, guild_wars.history[1].opponent_name)
        self.assertEqual(491, guild_wars.history[1].opponent_score)
        self.assertEqual(500, guild_wars.history[1].score_limit)
        self.assertEqual(guild_wars.name, guild_wars.history[1].winner)

    def test_guild_wars_from_content_empty(self):
        """Testing parsing the guild wars of a guild that has never been in a war"""
        content = self.load_resource(FILE_GUILD_WAR_EMPTY)
        guild_wars = GuildWars.from_content(content)

        self.assertEqual("Redd Alliance", guild_wars.name)
        self.assertIsNone(guild_wars.current)
        self.assertFalse(guild_wars.history)

    def test_guild_wars_from_content_unactive_history(self):
        """Testing parsing the guild wars of a war currently not in war and with war history."""
        content = self.load_resource(FILE_GUILD_WAR_UNACTIVE_HISTORY)
        guild_wars = GuildWars.from_content(content)

        self.assertIsInstance(guild_wars, GuildWars)
        self.assertEqual("Dinastia de Perrones", guild_wars.name)
        self.assertIsNone(guild_wars.current)

        self.assertEqual(1, len(guild_wars.history))

        self.assertEqual(guild_wars.name, guild_wars.history[0].guild_name)
        self.assertEqual(0, guild_wars.history[0].guild_score)
        self.assertEqual(None, guild_wars.history[0].opponent_name)
        self.assertEqual(0, guild_wars.history[0].opponent_score)
        self.assertEqual(1000, guild_wars.history[0].score_limit)
        self.assertTrue(guild_wars.history[0].surrender)

    # endregion
