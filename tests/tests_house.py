import datetime
import json

import tests.tests_character
from tests.tests_tibiapy import TestTibiaPy
from tibiapy import House, InvalidContent
from tibiapy.enums import HouseStatus, HouseType

FILE_HOUSE_FULL = "house/tibiacom_full.txt"
FILE_HOUSE_STATUS_TRANSFER = "house/tibiacom_status_transfer.txt"
FILE_HOUSE_STATUS_NO_BIDS = "house/tibiacom_status_no_bids.txt"
FILE_HOUSE_STATUS_WITH_BIDS = "house/tibiacom_status_with_bids.txt"
FILE_HOUSE_STATUS_RENTED = "house/tibiacom_status_rented.txt"
FILE_HOUSE_NOT_FOUND = "house/tibiacom_not_found.txt"

FILE_HOUSE_TIBIADATA = "house/tibiadata.json"
FILE_HOUSE_TIBIADATA_NOT_FOUND = "house/tibiadata_not_found.json"


class TestsHouse(TestTibiaPy):
    def setUp(self):
        self.guild = {}

    @staticmethod
    def _get_resource(resource):
        return TestTibiaPy._load_resource(resource)

    def testHouse(self):
        content = self._get_resource(FILE_HOUSE_FULL)
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
        self.assertEqual(house.highest_bid, 0)

        house_json_raw = house.to_json()
        house_json = json.loads(house_json_raw)
        self.assertEqual(house.image_url, house_json["image_url"])

    def testHouseStatusTransferred(self):
        house = House("Name")
        content = self._get_resource(FILE_HOUSE_STATUS_TRANSFER)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.RENTED)
        self.assertEqual(house.owner, "Xenaris mag")
        self.assertEqual(house.transferee, "Ivarr Bezkosci")
        self.assertIsNotNone(house.transferee_url)
        self.assertTrue(house.transfer_accepted)
        self.assertEqual(house.transfer_price, 850000)

    def testHouseStatusRented(self):
        house = House("Name")
        content = self._get_resource(FILE_HOUSE_STATUS_RENTED)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.RENTED)
        self.assertEqual(house.owner, "Thorcen")
        self.assertIsInstance(house.paid_until, datetime.datetime)

    def testHouseStatusWithBids(self):
        house = House("Name")
        content = self._get_resource(FILE_HOUSE_STATUS_WITH_BIDS)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertIsNone(house.owner)
        self.assertEqual(house.highest_bid, 15000)
        self.assertEqual(house.highest_bidder, "King of Bosnia")
        self.assertIsInstance(house.auction_end, datetime.datetime)

    def testHouseStatusWithoutBids(self):
        house = House("Name")
        content = self._get_resource(FILE_HOUSE_STATUS_NO_BIDS)
        house._parse_status(content)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertIsNone(house.auction_end)

    def testHouseNotFound(self):
        content = self._get_resource(FILE_HOUSE_NOT_FOUND)
        house = House.from_content(content)

        self.assertIsNone(house)

    def testHouseUnrelated(self):
        content = self._get_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            House.from_content(content)

    def testHouseTibiaData(self):
        content = self._get_resource(FILE_HOUSE_TIBIADATA)
        house = House.from_tibiadata(content)

        self.assertIsInstance(house, House)
        self.assertEqual(house.id, 32012)
        self.assertEqual(house.world, "Gladera")
        self.assertEqual(house.type, HouseType.GUILDHALL)
        self.assertEqual(house.size, 7)
        self.assertEqual(house.status, HouseStatus.AUCTIONED)
        self.assertIsNone(house.owner)

    def testHouseTibiaDataNotFound(self):
        content = self._get_resource(FILE_HOUSE_TIBIADATA_NOT_FOUND)
        house = House.from_tibiadata(content)

        self.assertIsNone(house)

    def testHouseTibiaDataInvalid(self):
        with self.assertRaises(InvalidContent):
            House.from_tibiadata("<p>Not json</p>")

    def testGuildTibiaDataUnrelated(self):
        content = self._get_resource(tests.tests_character.FILE_CHARACTER_TIBIADATA)
        with self.assertRaises(InvalidContent):
            House.from_tibiadata(content)
