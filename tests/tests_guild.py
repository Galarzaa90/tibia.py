import datetime
import unittest

import tests.tests_character
from tests.tests_tibiapy import TestCommons
from tibiapy import Guild, GuildHouse, GuildInvite, GuildMember, InvalidContent, ListedGuild

FILE_GUILD_FULL = "guild/tibiacom_full.txt"
FILE_GUILD_NOT_FOUND = "guild/tibiacom_not_found.txt"
FILE_GUILD_INFO_COMPLETE = "guild/tibiacom_info_complete.txt"
FILE_GUILD_INFO_MINIMUM = "guild/tibiacom_info_minimum.txt"
FILE_GUILD_INFO_DISBANDING = "guild/tibiacom_info_disbanding.txt"
FILE_GUILD_INFO_FORMATION = "guild/tibiacom_info_formation.txt"
FILE_GUILD_LIST = "guild/tibiacom_list.txt"
FILE_GUILD_LIST_NOT_FOUND = "guild/tibiacom_list_not_found.txt"

FILE_GUILD_TIBIADATA = "guild/tibiadata.json"
FILE_GUILD_TIBIADATA_NOT_FOUND = "guild/tibiadata_not_found.json"
FILE_GUILD_TIBIADATA_DISBANDING = "guild/tibiadata_disbanding.json"
FILE_GUILD_TIBIADATA_INVITED = "guild/tibiadata_invited.json"
FILE_GUILD_TIBIADATA_LIST = "guild/tibiadata_list.json"
FILE_GUILD_TIBIADATA_LIST_NOT_FOUND = "guild/tibiadata_list_not_found.json"


class TestsGuild(TestCommons, unittest.TestCase):
    def setUp(self):
        self.guild = Guild()

    def test_guild_from_content(self):
        """Testing parsing a guild"""
        content = self._load_resource(FILE_GUILD_FULL)
        guild = Guild.from_content(content)
        self.assertIsInstance(guild, Guild, "Guild should be a Guild object.")
        self.assertEqual(guild.url, Guild.get_url(guild.name))
        self.assertEqual(guild.url_tibiadata, Guild.get_url_tibiadata(guild.name))
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

        self.assertIsInstance(guild.guildhall, GuildHouse)
        self.assertEqual(guild.guildhall.owner, guild.members[0].name)
        self.assertEqual(guild.guildhall.world, guild.world)
        self.assertIsInstance(guild.guildhall.paid_until_date, datetime.date)

    def test_guild_from_content_not_found(self):
        """Testing parsing a non existent guild"""
        content = self._load_resource(FILE_GUILD_NOT_FOUND)
        guild = Guild.from_content(content)
        self.assertIsNone(guild)

    def test_guild_from_content_unrelated(self):
        """Testing parsing an unrelated tibiacom section"""
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            Guild.from_content(content)

    def test_guild_from_content_complete_info(self):
        """Testing parsing a guild with all information possible"""
        content = self._load_parsed_resource(FILE_GUILD_INFO_COMPLETE)
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
        content = self._load_parsed_resource(FILE_GUILD_INFO_MINIMUM)
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

    def test_guild_from_content_disbanding(self):
        """Testing parsing a guild that is disbanding"""
        content = self._load_parsed_resource(FILE_GUILD_INFO_DISBANDING)
        self.guild._parse_guild_info(content)
        self.assertTrue(self.guild.active, "Guild should be active")

        self.guild._parse_guild_disband_info(content)
        self.assertIsNotNone(self.guild.disband_condition, "Guild should have a disband warning")
        self.assertEqual(self.guild.disband_date, datetime.date(2018, 8, 17), "Guild should have disband date")

    def test_guild_from_content_formation(self):
        """Testing parsing a guild that is in formation"""
        content = self._load_parsed_resource(FILE_GUILD_INFO_FORMATION)
        Guild._parse_guild_info(self.guild, content)
        self.assertFalse(self.guild["active"], "Guild should not be active")

        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNotNone(self.guild.disband_condition, "Guild should have a disband warning")
        self.assertEqual(self.guild.disband_date, datetime.date(2018, 8, 16), "Guild should have disband date")

    def test_listed_guild_from_content(self):
        """Testing parsing the list of guilds of a world"""
        content = self._load_resource(FILE_GUILD_LIST)
        guilds = ListedGuild.list_from_content(content)
        self.assertTrue(guilds)
        self.assertIsNotNone(ListedGuild.get_world_list_url(guilds[0].world))
        self.assertEqual("Zuna", guilds[0].world)
        self.assertTrue(guilds[0].active)
        self.assertFalse(guilds[-1].active)

    def test_listed_guild_from_content_not_found(self):
        """Testing parsing the guild list of a world that doesn't exist"""
        content = self._load_resource(FILE_GUILD_LIST_NOT_FOUND)
        guilds = ListedGuild.list_from_content(content)
        self.assertIsNone(guilds)

    def test_listed_guild_from_content_unrelated(self):
        """Testing parsing and unrelated section"""
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
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

    def test_guild_from_tibiadata(self):
        """Testing parsing a guild from TibiaData"""
        content = self._load_resource(FILE_GUILD_TIBIADATA)
        guild = Guild.from_tibiadata(content)

        self.assertIsInstance(guild, Guild)
        self.assertTrue(guild.open_applications)
        self.assertIsNotNone(guild.guildhall)
        self.assertEqual(guild.founded, datetime.date(2002, 2, 18))
        self.assertIsInstance(guild.guildhall, GuildHouse)
        self.assertEqual(guild.guildhall.world, guild.world)
        self.assertIsNotNone(guild.logo_url)

    def test_guild_from_tibiadata_not_found(self):
        """Testing parsing a non existent guild"""
        content = self._load_resource(FILE_GUILD_TIBIADATA_NOT_FOUND)
        guild = Guild.from_tibiadata(content)
        self.assertIsNone(guild)

    def test_guild_from_tibiadata_disbanding(self):
        """Testing parsing a disbanding guild from TibiaData"""
        content = self._load_resource(FILE_GUILD_TIBIADATA_DISBANDING)
        guild = Guild.from_tibiadata(content)
        self.assertIsNotNone(guild.disband_condition)
        self.assertEqual(guild.disband_date, datetime.date(2018, 12, 26))

    def test_guild_from_tibiadata_with_invites(self):
        """Testing parsing a guild with invites"""
        content = self._load_resource(FILE_GUILD_TIBIADATA_INVITED)
        guild = Guild.from_tibiadata(content)
        self.assertTrue(len(guild.invites) > 0)
        self.assertIsInstance(guild.invites[0], GuildInvite)

    def test_guild_from_tibiadata_invalid_json(self):
        """Testing parsing an invalid json"""
        with self.assertRaises(InvalidContent):
            Guild.from_tibiadata("<html><p>definitely not a json string</p></html>")

    def test_guild_from_tibiadata_unrelated_section(self):
        """Testing parsing a different TibiaData json"""
        content = self._load_resource(tests.tests_character.FILE_CHARACTER_TIBIADATA)
        with self.assertRaises(InvalidContent):
            Guild.from_tibiadata(content)

    def test_listed_guild_from_tibiadata(self):
        """Testing parsing a guild list from TibiaData"""
        content = self._load_resource(FILE_GUILD_TIBIADATA_LIST)
        guilds = ListedGuild.list_from_tibiadata(content)
        self.assertTrue(guilds)
        self.assertIsNotNone(ListedGuild.get_world_list_url_tibiadata(guilds[0].world))
        self.assertEqual("Zunera", guilds[0].world)
        self.assertIsInstance(guilds[0], ListedGuild)
        self.assertTrue(guilds[0].active)
        self.assertFalse(guilds[-1].active)

    def test_listed_guild_from_tibiadata_not_found(self):
        """Testing parsing a non existent guild"""
        content = self._load_resource(FILE_GUILD_TIBIADATA_LIST_NOT_FOUND)
        guilds = ListedGuild.list_from_tibiadata(content)
        # There's no way to tell if the searched world doesn't exist or has no guilds
        self.assertEqual(guilds, [])

    def test_listed_guild_from_tibiadata_unrelated_section(self):
        """Testing parsing an unrelated section"""
        content = self._load_resource(tests.tests_character.FILE_CHARACTER_TIBIADATA)
        with self.assertRaises(InvalidContent):
            ListedGuild.list_from_tibiadata(content)

    def test_listed_guild_from_tibiadata_invalid_json(self):
        """Testing parsing an invalid json"""
        with self.assertRaises(InvalidContent):
            ListedGuild.list_from_tibiadata("<b>Not JSON</b>")
