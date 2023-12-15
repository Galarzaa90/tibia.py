from tests.tests_tibiapy import TestCommons
from tibiapy import InvalidContentError
from tibiapy.enums import HouseOrder, HouseStatus, HouseType
from tibiapy.models import House, HouseEntry, HousesSection
from tibiapy.parsers import HouseParser, HousesSectionParser
from tibiapy.urls import get_house_url

FILE_HOUSE_RENTED = "house/houseRented.txt"
FILE_HOUSE_RENTED_ACCEPTED_TRANSFER = "house/houseRentedAcceptedTransfer.txt"
FILE_HOUSE_AUCTION_WITH_BIDS = "house/houseAuctionedWithBids.txt"
FILE_HOUSE_AUCTION_WITHOUT_BIDS = "house/houseAuctionedWithoutBids.txt"
FILE_HOUSE_NOT_FOUND = "house/houseNotFound.txt"

FILE_HOUSE_LIST = "housesSection/housesSection.txt"
FILE_HOUSE_LIST_NOT_FOUND = "housesSection/housesSectionNotFound.txt"
FILE_HOUSE_LIST_EMPTY = "housesSection/housesSectionEmpty.txt"
FILE_HOUSE_SECTION_AUCTIONED_HOUSES = "housesSection/housesSectionWithAuctionedHouses.txt"


class TestsHouse(TestCommons):

    # region House Tests
    def test_house_parser_from_content(self):
        """Testing parsing a house"""
        content = self.load_resource(FILE_HOUSE_RENTED)
        house = HouseParser.from_content(content)

        self.assertIsInstance(house, House)
        self.assertIsNotNone(house.name)
        self.assertIsInstance(house.beds, int)
        self.assertIsInstance(house.rent, int)
        self.assertEqual(HouseStatus.RENTED, house.status)
        self.assertEqual(house.url, get_house_url(house.world, house.id))
        self.assertIsNotNone(house.owner)
        self.assertIsNotNone(house.owner_url)
        self.assertIsNone(house.highest_bidder)
        self.assertIsNone(house.highest_bidder_url)

    def test_house_parser_from_content_rented_accepted_transfer(self):
        content = self.load_resource(FILE_HOUSE_RENTED_ACCEPTED_TRANSFER)

        house = HouseParser.from_content(content)

        self.assertIsNotNone(house)
        self.assertEqual(HouseStatus.RENTED, house.status)
        self.assertIsNotNone(house.owner)
        self.assertIsNotNone(house.owner_url)
        self.assertIsNotNone(house.transfer_recipient)
        self.assertIsNotNone(house.transferee_url)
        self.assertIsNotNone(house.transfer_date)
        self.assertIsNotNone(house.transfer_price)
        self.assertTrue(house.transfer_accepted)

    def test_house_parser_from_content_auction_with_bids(self):
        content = self.load_resource(FILE_HOUSE_AUCTION_WITH_BIDS)

        house = HouseParser.from_content(content)

        self.assertIsNotNone(house)
        self.assertEqual(HouseStatus.AUCTIONED, house.status)
        self.assertIsNone(house.owner)
        self.assertIsNone(house.owner_url)
        self.assertIsNotNone(house.highest_bidder)
        self.assertIsNotNone(house.highest_bid)
        self.assertIsNotNone(house.auction_end)

    def test_house_parser_from_content_auction_without_bids(self):
        content = self.load_resource(FILE_HOUSE_AUCTION_WITHOUT_BIDS)

        house = HouseParser.from_content(content)

        self.assertIsNotNone(house)
        self.assertEqual(HouseStatus.AUCTIONED, house.status)
        self.assertIsNone(house.owner)
        self.assertIsNone(house.owner_url)
        self.assertIsNone(house.highest_bidder)
        self.assertIsNone(house.highest_bid)
        self.assertIsNone(house.auction_end)

    def test_house_parser_from_content_not_found(self):
        """Testing parsing a house that doesn't exist"""
        content = self.load_resource(FILE_HOUSE_NOT_FOUND)
        house = HouseParser.from_content(content)

        self.assertIsNone(house)

    def test_house_parser_from_content_unrelated(self):
        """Testing parsing an unrelated section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            HouseParser.from_content(content)

    # endregion

    # region Houses Section Tests

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

    def test_houses_section_parser_from_content_with_auctioned_houses(self):
        """Testing parsing an empty house list"""
        content = self.load_resource(FILE_HOUSE_SECTION_AUCTIONED_HOUSES)

        houses_section = HousesSectionParser.from_content(content)

        self.assertIsInstance(houses_section, HousesSection)

        def test_house_entry_auction_started(house: HouseEntry):
            self.assertEqual(HouseStatus.AUCTIONED, house.status)
            self.assertIsNotNone(house.highest_bid)
            self.assertIsNotNone(house.time_left)

        def test_house_entry_auction_not_started(house: HouseEntry):
            self.assertEqual(HouseStatus.AUCTIONED, house.status)
            self.assertIsNone(house.highest_bid)
            self.assertIsNone(house.time_left)

        self.assertForAtLeastOne(houses_section.entries, test_house_entry_auction_not_started)
        self.assertForAtLeastOne(houses_section.entries, test_house_entry_auction_started)

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
        with self.assertRaises(InvalidContentError):
            HousesSectionParser.from_content(content)

    # endregion
