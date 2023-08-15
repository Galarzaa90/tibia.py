import datetime
import json

from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContent
from tibiapy.builders.house import HouseBuilder
from tibiapy.enums import HouseOrder, HouseStatus, HouseType
from tibiapy.models import House, HousesSection, HouseEntry
from tibiapy.parsers.house import HouseParser, HousesSectionParser
from tibiapy.urls import get_house_url

FILE_HOUSE_RENTED = "house/houseRented.txt"
FILE_HOUSE_STATUS_TRANSFER = "house/houseStatusTransferred.txt"
FILE_HOUSE_STATUS_NO_BIDS = "house/houseStatusNoBids.txt"
FILE_HOUSE_STATUS_WITH_BIDS = "house/houseAuctionedWithBids.txt"
FILE_HOUSE_STATUS_RENTED = "house/houseStatusRented.txt"
FILE_HOUSE_NOT_FOUND = "house/houseNotFound.txt"
FILE_HOUSE_LIST = "house/housesSection.txt"
FILE_HOUSE_LIST_NOT_FOUND = "house/housesSectionNotFound.txt"
FILE_HOUSE_LIST_EMPTY = "house/housesSectionEmpty.txt"


class TestsHouse(TestCommons):
    def test_house_parser_from_content(self):
        """Testing parsing a house"""
        content = self.load_resource(FILE_HOUSE_RENTED)
        house = HouseParser.from_content(content)

        self.assertIsInstance(house, House)
        self.assertEqual("Sorcerer's Avenue Labs 2c", house.name)
        self.assertEqual(2, house.beds)
        self.assertTrue(50_000, house.rent)
        self.assertEqual(HouseStatus.RENTED, house.status)
        self.assertEqual(house.url, get_house_url(house.world, house.id))
        self.assertIsNotNone(house.owner)
        self.assertIsNotNone(house.owner_url)
        self.assertIsNone(house.highest_bidder)
        self.assertIsNone(house.highest_bidder_url)

        house_json_raw = house.model_dump_json()
        house_json = json.loads(house_json_raw)
        self.assertEqual(house.image_url, house_json["image_url"])

    def test_house_parser_from_content_transferred(self):
        """Testing parsing a house being transferred"""
        house = HouseBuilder().name("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_TRANSFER)
        HouseParser._parse_status(house, content)
        self.assertEqual(house._status, HouseStatus.RENTED)
        self.assertEqual(house._owner, "Xenaris mag")
        self.assertEqual(house._transfer_recipient, "Ivarr Bezkosci")
        self.assertTrue(house._transfer_accepted)
        self.assertEqual(house._transfer_price, 850000)

    def test_house_parse_status_rented(self):
        """Testing parsing a rented status"""
        house = HouseBuilder().name("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_RENTED)
        HouseParser._parse_status(house, content)
        self.assertEqual(house._status, HouseStatus.RENTED)
        self.assertEqual(house._owner, "Thorcen")
        self.assertIsInstance(house._paid_until, datetime.datetime)

    def test_house_parser_from_content_house_with_bids(self):
        """Testing parsing a house status with bids"""
        content = self.load_resource(FILE_HOUSE_STATUS_WITH_BIDS)

        house = HouseParser.from_content(content)

        self.assertEqual(HouseStatus.AUCTIONED, house.status)
        self.assertEqual(80_000, house.rent)
        self.assertIsNone(house.owner)
        self.assertEqual(0, house.highest_bid)
        self.assertIsNotNone(house.highest_bidder)
        self.assertIsNotNone(house.auction_end)

    def test_house_parse_status_without_bids(self):
        """Testing parsing the status of a house with no bids"""
        house = HouseBuilder().name("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_NO_BIDS)
        HouseParser._parse_status(house, content)
        self.assertEqual(house._status, HouseStatus.AUCTIONED)
        self.assertIsNone(house._auction_end)

    def test_house_parser_from_content_not_found(self):
        """Testing parsing a house that doesn't exist"""
        content = self.load_resource(FILE_HOUSE_NOT_FOUND)
        house = HouseParser.from_content(content)

        self.assertIsNone(house)

    def test_house_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            HouseParser.from_content(content)

    def test_houses_section_parser_from_content(self):
        """Testing parsing the house list of a world and city"""
        content = self.load_resource(FILE_HOUSE_LIST)
        house_results = HousesSectionParser.from_content(content)

        self.assertIsInstance(house_results, HousesSection)
        self.assertEqual("Carlin", house_results.town)
        self.assertEqual("Alumbra", house_results.world)
        self.assertEqual(HouseStatus.RENTED, house_results.status)
        self.assertEqual(HouseType.HOUSE, house_results.house_type)
        self.assertEqual(HouseOrder.RENT, house_results.order)

        houses = house_results.entries
        self.assertIsInstance(houses, list)
        self.assertGreater(len(houses), 0)
        self.assertIsInstance(houses[0], HouseEntry)
        self.assertEqual(houses[0].town, "Carlin")
        self.assertEqual(houses[0].type, HouseType.HOUSE)
        self.assertEqual(houses[0].status, HouseStatus.RENTED)
        self.assertIsInstance(houses[0].id, int)

        self.assertEqual(houses[25].status, HouseStatus.RENTED)

    def test_houses_section_parser_from_content_empty(self):
        """Testing parsing an empty house list"""
        content = self.load_resource(FILE_HOUSE_LIST_EMPTY)
        house_results = HousesSectionParser.from_content(content)

        self.assertIsInstance(house_results, HousesSection)
        self.assertEqual("Edron", house_results.town)
        self.assertEqual("Antica", house_results.world)
        self.assertEqual(HouseStatus.AUCTIONED, house_results.status)
        self.assertEqual(HouseType.GUILDHALL, house_results.house_type)
        self.assertEqual(HouseOrder.RENT, house_results.order)
        self.assertIsEmpty(house_results.entries)


    def test_houses_section_parser_from_content_not_found(self):
        """Testing parsing an empty house list"""
        content = self.load_resource(FILE_HOUSE_LIST_NOT_FOUND)
        results = HousesSectionParser.from_content(content)
        self.assertIsInstance(results, HousesSection)
        self.assertIsEmpty(results.entries)

    def test_houses_section_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            HousesSectionParser.from_content(content)

