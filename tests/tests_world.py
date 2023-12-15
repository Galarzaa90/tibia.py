import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.enums import BattlEyeType, PvpType, TransferType, WorldLocation
from tibiapy.models import World, WorldEntry, WorldOverview
from tibiapy.parsers import WorldOverviewParser, WorldParser
from tibiapy.urls import get_world_url

FILE_WORLD_ONLINE = "world/worldOnline.txt"
FILE_WORLD_YELLOW_BE = "world/worldYellowBattlEye.txt"
FILE_WORLD_GREEN_BE = "world/worldGreenBattlEye.txt"
FILE_WORLD_UNPROTECTED = "world/worldUnprotected.txt"
FILE_WORLD_NO_TITLES = "world/worldNoTitles.txt"
FILE_WORLD_OFFLINE = "world/worldOffline.txt"
FILE_WORLD_NOT_FOUND = "world/worldNotFound.txt"
FILE_WORLD_OVERVIEW_ONLINE = "worldOverview/worldOverviewOnline.txt"
FILE_WORLD_OVERVIEW_OFFLINE = "worldOverview/worldOverviewOffline.txt"


class TestWorld(TestCommons):

    # region World Tests
    def test_world_parser_from_content_online(self):
        """Testing parsing a world with full information"""
        content = self.load_resource(FILE_WORLD_ONLINE)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertTrue(world.is_online)
        self.assertEqual(world.record_count, 531)
        self.assertSizeEquals(world.online_players, world.online_count)
        self.assertEqual(get_world_url(world.name), world.url)

    def test_world_parser_from_content_yellow_battleye(self):
        """Testing parsing a world with yellow BattlEye."""
        content = self.load_resource(FILE_WORLD_YELLOW_BE)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertIsInstance(world.battleye_since, datetime.date)
        self.assertEqual(BattlEyeType.YELLOW, world.battleye_type)
        self.assertEqual(BattlEyeType.PROTECTED, world.battleye_type)
        self.assertTrue(world.is_battleye_protected)

    def test_world_parser_from_content_green_battleye(self):
        """Testing parsing a world with green BattlEye."""
        content = self.load_resource(FILE_WORLD_GREEN_BE)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertIsNone(world.battleye_since)
        self.assertEqual(BattlEyeType.GREEN, world.battleye_type)
        self.assertEqual(BattlEyeType.INITIALLY_PROTECTED, world.battleye_type)
        self.assertTrue(world.is_battleye_protected)

    def test_world_parser_from_content_no_battleye_protection(self):
        """Testing parsing a world without BattlEye protection."""
        content = self.load_resource(FILE_WORLD_UNPROTECTED)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertIsNone(world.battleye_since)
        self.assertEqual(BattlEyeType.UNPROTECTED, world.battleye_type)
        self.assertFalse(world.is_battleye_protected)

    def test_world_parser_from_content_experimental(self):
        """Testing parsing an experimental world"""
        content = self.load_resource(FILE_WORLD_UNPROTECTED)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertTrue(world.is_experimental)

    def test_world_parser_from_content_no_quest_titles(self):
        """Testing parsing a world without BattlEye protection."""
        content = self.load_resource(FILE_WORLD_NO_TITLES)

        world = WorldParser.from_content(content)

        self.assertIsEmpty(world.world_quest_titles)

    def test_world_parser_from_content_offline(self):
        """Testing parsing an offline world"""
        content = self.load_resource(FILE_WORLD_OFFLINE)

        world = WorldParser.from_content(content)

        self.assertIsInstance(world, World)
        self.assertFalse(world.is_online)
        self.assertEqual(world.online_count, 0)
        self.assertEqual(len(world.online_players), world.online_count)

    def test_world_parser_from_content_not_found(self):
        """Testing parsing a world that doesn't exist"""
        content = self.load_resource(FILE_WORLD_NOT_FOUND)

        world = WorldParser.from_content(content)

        self.assertIsNone(world)

    def test_world_parser_from_content_unrelated_section(self):
        """Testing parsing a world using an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            WorldParser.from_content(content)

    # endregion

    # region WorldOverview Tests
    def test_world_overview_from_content(self):
        """Testing parsing world overview"""
        content = self.load_resource(FILE_WORLD_OVERVIEW_ONLINE)

        world_overview = WorldOverviewParser.from_content(content)

        self.assertIsInstance(world_overview, WorldOverview)
        self.assertGreater(len(world_overview.worlds), 0)
        self.assertGreater(world_overview.total_online, 0)
        self.assertIsNotNone(world_overview.record_date)
        self.assertIsNotNone(world_overview.record_count)

    def test_world_overview_from_content_offline(self):
        """Testing parsing world overview with offline worlds"""
        content = self.load_resource(FILE_WORLD_OVERVIEW_OFFLINE)

        world_overview = WorldOverviewParser.from_content(content)

        self.assertEqual(world_overview.record_count, 64028)
        self.assertIsInstance(world_overview.record_date, datetime.datetime)
        self.assertIsNotEmpty(world_overview.worlds)
        self.assertIsInstance(world_overview.worlds[0], WorldEntry)
        self.assertIsInstance(world_overview.worlds[0].pvp_type, PvpType)
        self.assertIsInstance(world_overview.worlds[0].transfer_type, TransferType)
        self.assertIsInstance(world_overview.worlds[0].location, WorldLocation)
        self.assertIsInstance(world_overview.worlds[0].online_count, int)

    def test_world_overview_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibia section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)

        with self.assertRaises(InvalidContentError):
            WorldOverviewParser.from_content(content)
    # endregion
