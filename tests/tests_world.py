import json

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import World, WorldOverview

FILE_WORLD_FULL = "world_full.txt"
FILE_WORLD_FULL_OFFLINE = "world_full_off.txt"
FILE_WORLD_TIBIADATA = "world_tibiadata.txt"
FILE_WORLD_NOT_FOUND = "world_not_found.txt"

FILE_WORLD_LIST = "world_list.txt"
FILE_WORLD_LIST_OFFLINE = "world_list_offline.txt"
FILE_WORLD_LIST_TIBIADATA = "world_list_tibiadata.txt"


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

        world_json_raw = world.to_json()
        world_json = json.loads(world_json_raw)
        self.assertEqual(len(world.players_online), len(world_json["players_online"]))

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

    def testWorldOverview(self):
        content = self._get_parsed_content(FILE_WORLD_LIST_OFFLINE, False)
        worlds = WorldOverview.from_content(content)

        self.assertIsNotNone(WorldOverview.get_url())
        self.assertIsNotNone(WorldOverview.get_url_tibiadata())
        self.assertGreater(len(worlds.worlds), 0)
        self.assertGreater(worlds.total_online, 0)
        self.assertIsNotNone(worlds.record_date)
        self.assertIsNotNone(worlds.record_count)

    def testWorldOverviewOffline(self):
        content = self._get_parsed_content(FILE_WORLD_LIST_OFFLINE, False)
        worlds = WorldOverview.from_content(content)

        self.assertGreater(len(worlds.worlds), 0)
        self.assertIsNotNone(worlds.record_date)
        self.assertIsNotNone(worlds.record_count)

    def testWorldOverviewTibiaData(self):
        content = self._get_parsed_content(FILE_WORLD_LIST_TIBIADATA, False)
        worlds = WorldOverview.from_tibiadata(content)

        self.assertGreater(len(worlds.worlds), 0)
        self.assertIsNotNone(worlds.record_date)
        self.assertIsNotNone(worlds.record_count)

    def testWorldOverviewTibiaDataInvalidJson(self):
        worlds = WorldOverview.from_tibiadata("<html><b>Not a json string</b></html>")
        self.assertIsNone(worlds)
