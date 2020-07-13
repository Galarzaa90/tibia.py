import datetime
import json
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import House, InvalidContent, ListedHouse
from tibiapy.enums import HouseStatus, HouseType

FILE_HOUSE_FULL = "house/tibiacom_full.txt"
FILE_HOUSE_STATUS_TRANSFER = "house/tibiacom_status_transfer.txt"
FILE_HOUSE_STATUS_NO_BIDS = "house/tibiacom_status_no_bids.txt"
FILE_HOUSE_STATUS_WITH_BIDS = "house/tibiacom_status_with_bids.txt"
FILE_HOUSE_STATUS_RENTED = "house/tibiacom_status_rented.txt"
FILE_HOUSE_NOT_FOUND = "house/tibiacom_not_found.txt"
FILE_HOUSE_LIST = "house/tibiacom_list.txt"
FILE_HOUSE_LIST_NOT_FOUND = "house/tibiacom_list_not_found.txt"
FILE_HOUSE_LIST_EMPTY = "house/tibiacom_list_empty.txt"


class TestsHouse(TestCommons, unittest.TestCase):
    def setUp(self):
        self.guild = {}

    def test_house_from_content(self):
        """Testing parsing a house"""
        content = self.load_resource(FILE_HOUSE_FULL)
        house = House.from_content(content)

        self.assertIsInstance(house, House)
        self.assertEqual(house.name, "Sorcerer's Avenue Labs 2e")
        self.assertEqual(house.beds, 1)
        self.assertTrue(house.rent, 715)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertEqual(house.url, House.get_url(house.id, house.world))
        self.assertIsNone(house.owner)
        self.assertIsNone(house.owner_url)
        self.assertIsNotNone(house.highest_bidder)
        self.assertIsNotNone(house.highest_bidder_url)
        self.assertEqual(house.highest_bid, 0)

        house_json_raw = house.to_json()
        house_json = json.loads(house_json_raw)
        self.assertEqual(house.image_url, house_json["image_url"])

    def test_house_from_content_transferred(self):
        """Testing parsing a house being transferred"""
        house = House("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_TRANSFER)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.RENTED)
        self.assertEqual(house.owner, "Xenaris mag")
        self.assertEqual(house.transferee, "Ivarr Bezkosci")
        self.assertIsNotNone(house.transferee_url)
        self.assertTrue(house.transfer_accepted)
        self.assertEqual(house.transfer_price, 850000)

    def test_house_parse_status_rented(self):
        """Testing parsing a rented status"""
        house = House("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_RENTED)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.RENTED)
        self.assertEqual(house.owner, "Thorcen")
        self.assertIsInstance(house.paid_until, datetime.datetime)

    def test_house_parse_status_with_bids(self):
        """Testing parsing a house status with bids"""
        house = House("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_WITH_BIDS)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertIsNone(house.owner)
        self.assertEqual(house.highest_bid, 15000)
        self.assertEqual(house.highest_bidder, "King of Bosnia")
        self.assertIsInstance(house.auction_end, datetime.datetime)

    def test_house_parse_status_without_bids(self):
        """Testing parsing the status of a house with no bids"""
        house = House("Name")
        content = self.load_resource(FILE_HOUSE_STATUS_NO_BIDS)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertIsNone(house.auction_end)

    def test_house_from_content_not_found(self):
        """Testing parsing a house that doesn't exist"""
        content = self.load_resource(FILE_HOUSE_NOT_FOUND)
        house = House.from_content(content)

        self.assertIsNone(house)

    def test_house_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            House.from_content(content)

    def test_listed_house_from_content(self):
        """Testing parsing the house list of a world and city"""
        content = self.load_resource(FILE_HOUSE_LIST)
        houses = ListedHouse.list_from_content(content)

        self.assertIsInstance(houses, list)
        self.assertGreater(len(houses), 0)
        self.assertIsInstance(houses[0], ListedHouse)
        self.assertEqual(houses[0].town, "Carlin")
        self.assertEqual(houses[0].type, HouseType.HOUSE)
        self.assertEqual(houses[0].status, HouseStatus.RENTED)
        self.assertIsInstance(houses[0].id, int)
        self.assertIsNotNone(ListedHouse.get_list_url(houses[0].world, houses[0].town))

        self.assertEqual(houses[25].status, HouseStatus.RENTED)

    def test_listed_house_from_content_empty(self):
        """Testing parsing an empty house list"""
        content = self.load_resource(FILE_HOUSE_LIST_EMPTY)
        houses = ListedHouse.list_from_content(content)

        self.assertEqual(len(houses), 0)

    def test_listed_house_from_content_not_found(self):
        """Testing parsing an empty house list"""
        content = self.load_resource(FILE_HOUSE_NOT_FOUND)
        houses = ListedHouse.list_from_content(content)

        self.assertIsNone(houses)

    def test_listed_house_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            ListedHouse.list_from_content(content)

