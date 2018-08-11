import unittest
import os.path

from tibiapy import Guild

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")

GUILD = {}
PATH_GUILD_ACTIVE = "GuildActive.txt"
PATH_GOOD_GUILD_INFO = "good_guild_info.txt"


class TestTibiaPy(unittest.TestCase):

    def setUp(self):
        GUILD.clear()

    def testGuilds(self):
        with open(RESOURCES_PATH + PATH_GUILD_ACTIVE) as f:
            content = f.read()
        guild = Guild.from_content(content)
        self.assertTrue(guild.active)
        self.assertIsNotNone(guild.description)
        self.assertTrue(guild.members)
        self.assertIsInstance(guild.members[0].level, int)

    def testGuildNoDisbandInfo(self):
        Guild.parse_guild_disband_info(GUILD, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNone(GUILD["disband_condition"], "Guild should not be under disband warning")
        self.assertIsNone(GUILD["disband_date"], "Guild should not have disband date")

    def testGuildHasGuildhall(self):
        Guild.parse_guild_guildhall(GUILD, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        guildhall = GUILD["guildhall"]
        self.assertIsNotNone(guildhall, "Guild should have guildhall")
        self.assertEqual(guildhall["name"], "Sky Lane, Guild 1", "Guildhall should have name")
        self.assertEqual(guildhall["paid_until"], "Aug 26 2018", "Guildhall should have payment date")

    def testGuildHomepageOk(self):
        Guild.parse_guild_homepage(GUILD, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNotNone(GUILD["homepage"], "Guild homepage must exist")
        self.assertEqual("tibiammo.reddit.com", GUILD["homepage"])

    def testGuildApplicationsOpen(self):
        Guild.parse_guild_applications(GUILD, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertTrue(GUILD["open_applications"], "Guild should be open to applications")

    def testGuildInfoOk(self):
        Guild.parse_guild_info(GUILD, self._get_parsed_content(PATH_GOOD_GUILD_INFO))
        self.assertIsNotNone(GUILD["description"], "Guild description must exist")
        self.assertEqual("Gladera", GUILD["world"], "Incorrect world")
        self.assertEqual("Jul 23 2015", GUILD["founded"], "Incorrect founding date")
        self.assertTrue(GUILD["active"], "Guild should be active")

    @staticmethod
    def _get_parsed_content(resource):
        with open(RESOURCES_PATH + resource) as f:
            content = f.read()
        return Guild.beautiful_soup(content)
