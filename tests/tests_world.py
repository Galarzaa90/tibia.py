import datetime
import json
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent, TournamentWorldType, World, WorldOverview
from tibiapy.enums import PvpType, TransferType, WorldLocation
from tibiapy.world import ListedWorld

FILE_WORLD_FULL = "world/tibiacom_online.txt"
FILE_WORLD_FULL_OFFLINE = "world/tibiacom_offline.txt"
FILE_WORLD_TOURNAMENT = "world/tibiacom_tournament.txt"
FILE_WORLD_NOT_FOUND = "world/tibiacom_not_found.txt"
FILE_WORLD_LIST = "world/tibiacom_list_online.txt"
FILE_WORLD_LIST_OFFLINE = "world/tibiacom_list_offline.txt"


class TestWorld(TestCommons, unittest.TestCase):

    # region Tibia.com Tests
    def test_world_from_content_full(self):
        """Testing parsing a world with full information"""
        content = self.load_resource(FILE_WORLD_FULL)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Premia")
        self.assertEqual(world.status, "Online")
        self.assertEqual(world.record_count, 531)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "2002-04")
        self.assertEqual(world.creation_year, 2002)
        self.assertEqual(world.creation_month, 4)
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

    def test_world_from_content_offline(self):
        """Testing parsing an offline world"""
        content = self.load_resource(FILE_WORLD_FULL_OFFLINE, )
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertEqual(world.name, "Antica")
        self.assertEqual(world.status, "Offline")
        self.assertEqual(world.record_count, 1052)
        self.assertIsInstance(world.record_date, datetime.datetime)
        self.assertEqual(world.creation_date, "1997-01")
        self.assertEqual(world.creation_year, 1997)
        self.assertEqual(world.creation_month, 1)
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

    def test_world_from_content_not_found(self):
        """Testing parsing a world that doesn't exist"""
        content = self.load_resource(FILE_WORLD_NOT_FOUND)
        world = World.from_content(content)

        self.assertIsNone(world)

    def test_world_from_content_unrelated_section(self):
        """Testing parsing a world using an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            World.from_content(content)

    def test_world_from_content_tournament(self):
        """Testing parsing a tournament world"""
        content = self.load_resource(FILE_WORLD_TOURNAMENT)
        world = World.from_content(content)

        self.assertIsInstance(world, World)
        self.assertIsInstance(world.tournament_world_type, TournamentWorldType)
        self.assertEqual(world.tournament_world_type, TournamentWorldType.REGUlAR)
        self.assertEqual(world.record_count, 21)
        self.assertTrue(world.premium_only)
        self.assertFalse(world.world_quest_titles)

    # endregion

    # region Tibia.com WorldOverview Tests
    def test_world_overview_from_content(self):
        """Testing parsing world overview"""
        content = self.load_resource(FILE_WORLD_LIST)
        world_overview = WorldOverview.from_content(content)

        self.assertIsInstance(world_overview, WorldOverview)
        self.assertEqual(WorldOverview.get_url(), ListedWorld.get_list_url())
        self.assertGreater(len(world_overview.worlds), 0)
        self.assertGreater(world_overview.total_online, 0)
        self.assertIsNotNone(world_overview.record_date)
        self.assertIsNotNone(world_overview.record_count)
        self.assertEqual(len(world_overview.regular_worlds), 65)
        self.assertEqual(len(world_overview.tournament_worlds), 6)

        worlds = ListedWorld.list_from_content(content)
        self.assertEqual(len(world_overview.worlds), len(worlds))

    def test_world_overview_from_content_offline(self):
        """Testing parsing world overview with offline worlds"""
        content = self.load_resource(FILE_WORLD_LIST_OFFLINE)
        world_overview = WorldOverview.from_content(content)

        self.assertEqual(world_overview.record_count, 64028)
        self.assertIsInstance(world_overview.record_date, datetime.datetime)
        self.assertGreater(len(world_overview.worlds), 0)
        self.assertIsInstance(world_overview.worlds[0], ListedWorld)
        self.assertIsInstance(world_overview.worlds[0].pvp_type, PvpType)
        self.assertIsInstance(world_overview.worlds[0].transfer_type, TransferType)
        self.assertIsInstance(world_overview.worlds[0].location, WorldLocation)
        self.assertIsInstance(world_overview.worlds[0].online_count, int)

    def test_world_overview_from_content_unrelated(self):
        """Testing parsing an unrealted tibia section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            ListedWorld.list_from_content(content)
    # endregion
