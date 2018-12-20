import datetime
import json

import tests.tests_character
from tests.tests_tibiapy import TestTibiaPy
from tibiapy import InvalidContent, World, WorldOverview
from tibiapy.enums import PvpType, TransferType, WorldLocation
from tibiapy.world import ListedWorld

FILE_WORLD_FULL = "world/tibiacom_online.txt"
FILE_WORLD_FULL_OFFLINE = "world/tibiacom_offline.txt"
FILE_WORLD_NOT_FOUND = "world/tibiacom_not_found.txt"
FILE_WORLD_LIST = "world/tibiacom_list_online.txt"
FILE_WORLD_LIST_OFFLINE = "world/tibiacom_list_offline.txt"

FILE_WORLD_TIBIADATA = "world/tibiadata_online.json"
FILE_WORLD_TIBIADATA_OFFLINE = "world/tibiadata_offline.json"
FILE_WORLD_LIST_TIBIADATA = "world/tibiadata_list_online.json"
FILE_WORLD_LIST_TIBIADATA_OFFLINE = "world/tibiadata_list_offline.json"


class TestWorld(TestTibiaPy):
    def setUp(self):
        self.guild = {}

    @staticmethod
    def _load_parsed_resource(resource, beautiful_soup=True):
        content = TestTibiaPy._load_resource(resource)
        return World._beautiful_soup(content) if beautiful_soup else content

    def testWorld(self):
        content = self._load_parsed_resource(FILE_WORLD_FULL, False)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Premia")
        self.assertEqual(world.status, "Online")
        self.assertEqual(world.record_count, 531)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "04/02")
        self.assertEqual(world.location, WorldLocation.EUROPE)
        self.assertEqual(world.pvp_type, PvpType.OPEN_PVP)
        self.assertEqual(world.transfer_type, TransferType.REGULAR)
        self.assertEqual(len(world.world_quest_titles), 4)
        self.assertTrue(world.premium_only)
        self.assertTrue(world.battleye_protected)
        self.assertEqual(world.battleye_date, datetime.date(2017, 9, 5))
        self.assertFalse(world.experimental)
        self.assertEqual(len(world.online_players), world.online_count)
        self.assertEqual(World.get_url(world.name), world.url)

        world_json_raw = world.to_json()
        world_json = json.loads(world_json_raw)
        self.assertEqual(len(world.online_players), len(world_json["online_players"]))

    def testWorldOffline(self):
        content = self._load_parsed_resource(FILE_WORLD_FULL_OFFLINE, False)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Antica")
        self.assertEqual(world.status, "Offline")
        self.assertEqual(world.record_count, 1052)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "01/97")
        self.assertEqual(world.location, WorldLocation.EUROPE)
        self.assertEqual(world.pvp_type, PvpType.OPEN_PVP)
        self.assertEqual(world.transfer_type, TransferType.REGULAR)
        self.assertEqual(len(world.world_quest_titles), 5)
        self.assertFalse(world.premium_only)
        self.assertTrue(world.battleye_protected)
        self.assertEqual(world.battleye_date, datetime.date(2017, 8, 29))
        self.assertFalse(world.experimental)
        self.assertEqual(len(world.online_players), world.online_count)
        self.assertEqual(World.get_url(world.name), world.url)

    def testWorldNotFound(self):
        content = self._load_parsed_resource(FILE_WORLD_NOT_FOUND, False)
        world = World.from_content(content)

        self.assertIsNone(world)

    def testWorldUnrelated(self):
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            World.from_content(content)

    def testWorldOverview(self):
        content = self._load_parsed_resource(FILE_WORLD_LIST, False)
        worlds = ListedWorld.list_from_content(content)

        self.assertIsInstance(worlds, WorldOverview)
        self.assertIsNotNone(ListedWorld.get_list_url())
        self.assertIsNotNone(ListedWorld.get_list_url_tibiadata())
        self.assertGreater(len(worlds.worlds), 0)
        self.assertGreater(worlds.total_online, 0)
        self.assertIsNotNone(worlds.record_date)
        self.assertIsNotNone(worlds.record_count)

    def testWorldOverviewOffline(self):
        content = self._load_parsed_resource(FILE_WORLD_LIST_OFFLINE, False)
        world_overview = ListedWorld.list_from_content(content)

        self.assertEqual(world_overview.record_count, 64028)
        self.assertIsInstance(world_overview.record_date, datetime.datetime)
        self.assertGreater(len(world_overview.worlds), 0)
        self.assertIsInstance(world_overview.worlds[0], ListedWorld)
        self.assertIsInstance(world_overview.worlds[0].pvp_type, PvpType)
        self.assertIsInstance(world_overview.worlds[0].transfer_type, TransferType)
        self.assertIsInstance(world_overview.worlds[0].location, WorldLocation)
        self.assertIsInstance(world_overview.worlds[0].online_count, int)

    def testWorldTibiadata(self):
        content = self._load_parsed_resource(FILE_WORLD_TIBIADATA, False)
        world = World.from_tibiadata(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Zuna")
        self.assertEqual(world.status, "Online")
        self.assertEqual(world.record_count, 106)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "10/17")
        self.assertEqual(world.location, WorldLocation.EUROPE)
        self.assertEqual(world.pvp_type, PvpType.HARDCORE_PVP)
        self.assertEqual(world.transfer_type, TransferType.LOCKED)
        self.assertEqual(len(world.world_quest_titles), 1)
        self.assertFalse(world.premium_only)
        self.assertFalse(world.battleye_protected)
        self.assertIsNone(world.battleye_date)
        self.assertTrue(world.experimental)
        self.assertEqual(len(world.online_players), world.online_count)
        self.assertEqual(World.get_url_tibiadata(world.name), world.url_tibiadata)

    def testWorldTibiaDataOffline(self):
        content = self._load_parsed_resource(FILE_WORLD_TIBIADATA_OFFLINE, False)
        world = World.from_tibiadata(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Antica")
        self.assertEqual(world.record_count, 1052)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "01/97")
        self.assertEqual(world.location, WorldLocation.EUROPE)
        self.assertEqual(world.pvp_type, PvpType.OPEN_PVP)
        self.assertEqual(world.transfer_type, TransferType.REGULAR)
        self.assertEqual(len(world.world_quest_titles), 5)
        self.assertFalse(world.premium_only)
        self.assertTrue(world.battleye_protected)
        self.assertIsInstance(world.battleye_date, datetime.date)
        self.assertFalse(world.experimental)
        self.assertEqual(len(world.online_players), world.online_count)
        self.assertEqual(World.get_url_tibiadata(world.name), world.url_tibiadata)

    def testWorldTibiaDataInvalidJson(self):
        with self.assertRaises(InvalidContent):
            World.from_tibiadata("<html><b>Not a json string</b></html>")

    def testWorldTibiaDataUnrelated(self):
        with self.assertRaises(InvalidContent):
            World.from_tibiadata(self._load_resource(tests.tests_character.FILE_CHARACTER_TIBIADATA))

    def testWorldOverviewTibiaData(self):
        content = self._load_parsed_resource(FILE_WORLD_LIST_TIBIADATA, False)
        worlds = ListedWorld.list_from_tibiadata(content)

        self.assertIsInstance(worlds, list)
        self.assertGreater(len(worlds), 0)
        self.assertIsInstance(worlds[0], ListedWorld)
        self.assertIsInstance(worlds[0].pvp_type, PvpType)
        self.assertIsInstance(worlds[0].transfer_type, TransferType)
        self.assertIsInstance(worlds[0].location, WorldLocation)
        self.assertIsInstance(worlds[0].online_count, int)

    def testWorldOverviewTibiaDataOffline(self):
        content = self._load_parsed_resource(FILE_WORLD_LIST_TIBIADATA_OFFLINE, False)
        worlds = ListedWorld.list_from_tibiadata(content)

        self.assertIsInstance(worlds, list)
        self.assertGreater(len(worlds), 0)
        self.assertIsInstance(worlds[0], ListedWorld)
        self.assertIsInstance(worlds[0].pvp_type, PvpType)
        self.assertIsInstance(worlds[0].transfer_type, TransferType)
        self.assertIsInstance(worlds[0].location, WorldLocation)
        self.assertIsInstance(worlds[0].online_count, int)

    def testWorldOverviewTibiaDataInvalidJson(self):
        with self.assertRaises(InvalidContent):
            ListedWorld.list_from_tibiadata("<html><b>Not a json string</b></html>")
