import unittest
import os.path

from tibiapy import Guild

MY_PATH = os.path.abspath(os.path.dirname(__file__))
RESOURCES_PATH = os.path.join(MY_PATH, "resources/")
GUILD_ACTIVE = "GuildActive.txt"

class TestTibiaPy(unittest.TestCase):
    def testGuilds(self):        
        with open(RESOURCES_PATH + GUILD_ACTIVE) as f:
            content = f.read()
        guild = Guild.from_content(content)
        self.assertTrue(guild.active)
        self.assertIsNotNone(guild.description)
        self.assertTrue(guild.members)
        self.assertIsInstance(guild.members[0].level, int)