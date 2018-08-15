from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Guild, GuildMember

PATH_GUILD_ACTIVE = "GuildActive.txt"
PATH_GOOD_GUILD_INFO = "good_guild_info.txt"


class TestsGuild(TestTibiaPy):

    def setUp(self):
        self.guild = {}

    def testGuilds(self):
        guild = Guild.from_content(self._get_parsed_content(PATH_GUILD_ACTIVE, False))
        self.assertTrue(guild.active)
        self.assertIsNotNone(guild.description)
        self.assertTrue(guild.members)
        self.assertIsInstance(guild.members[0].level, int)

        mock_member = self._create_mock_member("Emperor Andrew", "Leader", None, "Elite Knight", 441, "", "Mar 20 2017")
        self._compare_member(mock_member, guild.members[0])

        mock_member = self._create_mock_member("Galarzaa Fidera", "Keeper", "Gallan", "Paladin", 285, "", "Nov 04 2015")
        self._compare_member(mock_member, guild.members[4])

        mock_member = self._create_mock_member("Tschas", "Mentor", None, "Druid", 205, "", "Jul 28 2016")
        self._compare_member(mock_member, guild.members[52])

    @staticmethod
    def _create_mock_member(name, rank, title, vocation, level, online, joined):
        return GuildMember(name, rank, level=level, vocation=vocation, title=title, online=online, joined=joined)

    def _compare_member(self, mock_member, member):
        self.assertEqual(mock_member.level, member.level)
        self.assertEqual(mock_member.name, member.name)
        self.assertEqual(mock_member.rank, member.rank)
        self.assertEqual(mock_member.title, member.title)
        self.assertEqual(mock_member.vocation, member.vocation)
        self.assertEqual(mock_member.joined, member.joined)

    def testGuildNoDisbandInfo(self):
        Guild._parse_guild_disband_info(self.guild, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNone(self.guild["disband_condition"], "Guild should not be under disband warning")
        self.assertIsNone(self.guild["disband_date"], "Guild should not have disband date")

    def testGuildHasGuildhall(self):
        Guild._parse_guild_guildhall(self.guild, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        guildhall = self.guild["guildhall"]
        self.assertIsNotNone(guildhall, "Guild should have guildhall")
        self.assertEqual(guildhall["name"], "Sky Lane, Guild 1")
        self.assertEqual(guildhall["paid_until"], "Aug 26 2018")

    def testGuildHomepageOk(self):
        Guild._parse_guild_homepage(self.guild, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNotNone(self.guild["homepage"], "Guild homepage must exist")
        self.assertEqual("tibiammo.reddit.com", self.guild["homepage"])

    def testGuildApplicationsOpen(self):
        Guild._parse_guild_applications(self.guild, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertTrue(self.guild["open_applications"], "Guild should be open to applications")

    def testGuildInfoOk(self):
        Guild._parse_guild_info(self.guild, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNotNone(self.guild["description"], "Guild description must exist")
        self.assertEqual("Gladera", self.guild["world"])
        self.assertEqual("Jul 23 2015", self.guild["founded"])
        self.assertTrue(self.guild["active"], "Guild should be active")

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
