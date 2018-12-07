from tests.tests_tibiapy import TestTibiaPy
from tibiapy import World

FILE_WORLD_FULL = "world_full.txt"
FILE_WORLD_FULL_OFFLINE = "world_full_off.txt"
FILE_WORLD_TIBIADATA = "world_tibiadata.txt"
FILE_WORLD_NOT_FOUND = "world_not_found.txt"

class TestsGuild(TestTibiaPy):
    def setUp(self):
        self.guild = {}

    @staticmethod
    def _get_parsed_content(resource, beautiful_soup=True):
        content = TestTibiaPy._load_resource(resource)
        return World._beautiful_soup(content) if beautiful_soup else content

    def testWorld(self):
        content = self._get_parsed_content(FILE_WORLD_FULL, False)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Premia")
        self.assertEqual(world.status, "Online")
        self.assertTrue(world.premium_only)
        self.assertEqual(len(world.players_online), world.online_count)
        self.assertEqual(World.get_url(world.name), world.url)

    def testWorldNotFound(self):
        content = self._get_parsed_content(FILE_WORLD_NOT_FOUND, False)
        world = World.from_content(content)

        self.assertIsNone(world)

    def testWorldOffline(self):
        content = self._get_parsed_content(FILE_WORLD_FULL_OFFLINE, False)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Antica")
        self.assertEqual(world.status, "Offline")
        self.assertEqual(world.online_count, 0)
        self.assertEqual(len(world.players_online), 0)

    def testWorldTibiadata(self):
        content = self._get_parsed_content(FILE_WORLD_TIBIADATA, False)
        world = World.from_tibiadata(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Zuna")
        self.assertEqual(world.status, "Online")
        self.assertFalse(world.premium_only)
        self.assertFalse(world.battleye_protected)
        self.assertEqual(world.online_count, len(world.players_online))
        self.assertEqual(World.get_url_tibiadata(world.name), world.url_tibiadata)

    def testWorldTibiaDataInvalidJson(self):
        world = World.from_tibiadata("<html><b>Not a json string</b></html>")
        self.assertIsNone(world)