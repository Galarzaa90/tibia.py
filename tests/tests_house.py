import json

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import House
from tibiapy.enums.tibia_enums import HouseStatus

FILE_HOUSE_FULL = "house_full.txt"
FILE_HOUSE_STATUS_TRANSFER = "house_status_transfer.txt"


class TestsGuild(TestTibiaPy):
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

    def testHouseStatusTransfer(self):
        content = self._get_resource(FILE_HOUSE_STATUS_TRANSFER)
        house = House("Name")
        house._parse_status(content)

        self.assertEqual(house.status, HouseStatus.RENTED)
        self.assertEqual(house.owner, "Xenaris mag")
        self.assertEqual(house.transferee, "Ivarr Bezkosci")
        self.assertIsNotNone(house.transferee_url)
        self.assertEqual(house.transfer_price, 850000)
