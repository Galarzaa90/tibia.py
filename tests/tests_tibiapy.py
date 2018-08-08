import unittest

from tibiapy import Guild


class TestTibiaPy(unittest.TestCase):
    def testGuilds(self):
        with open("resources/GuildActive.txt") as f:
            content = f.read()
        guild = Guild.from_content(content)
        self.assertTrue(guild.active)
        self.assertIsNotNone(guild.description)
        self.assertTrue(guild.members)
        self.assertIsInstance(guild.members[0].level, int)