import datetime

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Guild, GuildMember, GuildInvite

FILE_GUILD_FULL = "guild_full.txt"
FILE_GUILD_INFO_COMPLETE = "guild_info_complete.txt"
FILE_GUILD_INFO_MINIMUM = "guild_info_minimum.txt"
FILE_GUILD_INFO_DISBANDING = "guild_info_disbanding.txt"
FILE_GUILD_INFO_FORMATION = "guild_info_formation.txt"
FILE_GUILD_LIST = "guild_list.txt"

class TestsGuild(TestTibiaPy):
    def setUp(self):
        self.guild = {}

    @staticmethod
    def _get_parsed_content(resource, beautiful_soup=True):
        content = TestTibiaPy._load_resource(resource)
        return Guild._beautiful_soup(content) if beautiful_soup else content

    def testGuildFull(self):
        content = self._get_parsed_content(FILE_GUILD_FULL, False)
        guild = Guild.from_content(content)
        self.assertIsInstance(guild, Guild, "Guild should be a Guild object.")
        self.assertEqual(guild.url, Guild.get_url(guild.name))
        self.assertTrue(guild.active, "Guild should be active")
        self.assertIsInstance(guild.founded, datetime.date, "Guild founded date should be an instance of datetime.date")
        self.assertTrue(guild.open_applications, "Guild applications should be open")
        self.assertIsNotNone(guild.description, "Guild should have a description")
        self.assertTrue(guild.members, "Guild should have members")
        self.assertEqual(guild.member_count, len(guild.members))
        self.assertTrue(guild.invites, "Guild should have invites")
        self.assertIsInstance(guild.online_members, list, "Guild online members should be a list.")
        self.assertTrue(guild.ranks, "Guild ranks should not be empty.")
        for member in guild.members:
            self.assertIsInstance(member.level, int, "Member level should be an integer.")
            self.assertIsInstance(member.joined, datetime.date, "Member's joined date should be datetime.date.")
        for invited in guild.invites:
            self.assertIsNotNone(invited.name, "Invited character's name should not be None.")
            self.assertIsInstance(invited.date, datetime.date, "Invited character's date should be datetime.date.")

    def testGuildInfoComplete(self):
        content = self._get_parsed_content(FILE_GUILD_INFO_COMPLETE)
        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNone(self.guild["disband_condition"], "Guild should not be under disband warning")
        self.assertIsNone(self.guild["disband_date"], "Guild should not have disband date")

        Guild._parse_guild_guildhall(self.guild, content)
        guildhall = self.guild["guildhall"]
        self.assertIsNotNone(guildhall, "Guild should have guildhall")
        self.assertEqual(guildhall["name"], "Sky Lane, Guild 1")
        self.assertEqual(guildhall["paid_until"], "Aug 26 2018")

        Guild._parse_guild_homepage(self.guild, content)
        self.assertIsNotNone(self.guild["homepage"], "Guild homepage must exist")
        self.assertEqual("tibiammo.reddit.com", self.guild["homepage"])

        Guild._parse_guild_applications(self.guild, content)
        self.assertTrue(self.guild["open_applications"], "Guild should be open to applications")

        Guild._parse_guild_info(self.guild, content)
        self.assertIsNotNone(self.guild["description"], "Guild description must exist")
        self.assertEqual("Gladera", self.guild["world"])
        self.assertEqual("Jul 23 2015", self.guild["founded"])
        self.assertTrue(self.guild["active"], "Guild should be active")

    def testGuildInfoMinimum(self):
        content = self._get_parsed_content(FILE_GUILD_INFO_MINIMUM)
        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNone(self.guild["disband_condition"], "Guild should not be under disband warning")
        self.assertIsNone(self.guild["disband_date"], "Guild should not have disband date")

        Guild._parse_guild_guildhall(self.guild, content)
        guildhall = self.guild["guildhall"]
        self.assertIsNone(guildhall, "Guild should not have a guildhall")

        Guild._parse_guild_homepage(self.guild, content)
        self.assertIsNone(self.guild["homepage"], "Guild should not have a guildhall")

        Guild._parse_guild_info(self.guild, content)
        self.assertIsNone(self.guild["description"], "Guild description must not exist")
        self.assertEqual("Gladera", self.guild["world"])
        self.assertEqual("May 18 2018", self.guild["founded"])

    def testGuildInfoDisbanding(self):
        content = self._get_parsed_content(FILE_GUILD_INFO_DISBANDING)
        Guild._parse_guild_info(self.guild, content)
        self.assertTrue(self.guild["active"], "Guild should be active")

        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNotNone(self.guild["disband_condition"], "Guild should have a disband warning")
        self.assertEqual(self.guild["disband_date"], "Aug 17 2018", "Guild should have disband date")

    def testGuildInfoFormation(self):
        content = self._get_parsed_content(FILE_GUILD_INFO_FORMATION)
        Guild._parse_guild_info(self.guild, content)
        self.assertFalse(self.guild["active"], "Guild should not be active")

        Guild._parse_guild_disband_info(self.guild, content)
        self.assertIsNotNone(self.guild["disband_condition"], "Guild should have a disband warning")
        self.assertEqual(self.guild["disband_date"], "Aug 16 2018", "Guild should have disband date")

    def testGuildList(self):
        content = self._get_parsed_content(FILE_GUILD_LIST, False)
        guilds = Guild.list_from_content(content)
        self.assertTrue(guilds)
        self.assertIsNotNone(Guild.get_world_list_url(guilds[0].world))
        self.assertEqual("Zuna", guilds[0].world)
        self.assertTrue(guilds[0].active)
        self.assertFalse(guilds[-1].active)

    def testInvitationDate(self):
        guild = {"invites": []}
        name = "Tschas"
        date = "Invitation Date"
        values = name, date
        Guild._parse_invited_member(guild, values)
        self.assertIsNotNone(guild["invites"])
        self.assertListEqual(guild["invites"], [])

    def testInvitedMember(self):
        guild = {"invites": []}
        name = "Tschas"
        date = "Jun 20 2018"
        values = name, date
        Guild._parse_invited_member(guild, values)
        self.assertIsNotNone(guild["invites"])
        self.assertIsNotNone(guild["invites"][0])
        self.assertEqual(guild["invites"][0]["name"], name)
        self.assertEqual(guild["invites"][0]["date"], date)

    def testMemberJoinDate(self):
        self.assertIsInstance(GuildMember(joined="Jul 20 2018").joined, datetime.date)
        self.assertIsInstance(GuildMember(joined=datetime.date.today()).joined, datetime.date)
        self.assertIsInstance(GuildMember(joined=datetime.datetime.now()).joined, datetime.date)
        self.assertIsNone(GuildMember(joined=None).joined)
        self.assertIsNone(GuildMember(joined="Jul 20").joined)

    def testInviteDate(self):
        self.assertIsInstance(GuildInvite(date="Jul 20 2018").date, datetime.date)
        self.assertIsInstance(GuildInvite(date=datetime.date.today()).date, datetime.date)
        self.assertIsInstance(GuildInvite(date=datetime.datetime.now()).date, datetime.date)
        self.assertIsNone(GuildInvite(date=None).date)
        self.assertIsNone(GuildInvite(date="Jul 20").date)

    def testGuildFounded(self):
        self.assertIsInstance(Guild(founded="Jul 20 2018").founded, datetime.date)
        self.assertIsInstance(Guild(founded=datetime.date.today()).founded, datetime.date)
        self.assertIsInstance(Guild(founded=datetime.datetime.now()).founded, datetime.date)
        self.assertIsNone(Guild(founded=None).founded)
        self.assertIsNone(Guild(founded="Jul 20").founded)
