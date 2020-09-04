import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import AuctionDetails, AuctionOrder, AuctionOrderBy, BattlEyeTypeFilter, BidType, CharacterBazaar, \
    InvalidContent, PvpTypeFilter, \
    Sex, SkillFilter, \
    Vocation, VocationAuctionFilter

FILE_BAZAAR_CURRENT_EMPTY = "bazaar/tibiacom_history_empty.txt"
FILE_BAZAAR_CURRENT = "bazaar/tibiacom_current.txt"
FILE_BAZAAR_CURRENT_ALL_FILTERS = "bazaar/tibiacom_current_all_filters.txt"
FILE_BAZAAR_HISTORY = "bazaar/tibiacom_history.txt"
FILE_AUCTION_FINISHED = "bazaar/tibiacom_auction_finished.txt"


class TestBazaar(TestCommons, unittest.TestCase):
    def test_character_bazaar_from_content_current_no_filters_selected(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_CURRENT))

        self.assertIsNotNone(bazaar)
        self.assertEqual(300, bazaar.page)
        self.assertEqual(482, bazaar.total_pages)
        self.assertEqual(12031, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))
        self.assertIsNotNone(bazaar.url)

        auction = bazaar.entries[0]
        self.assertEqual(30237, auction.auction_id)
        self.assertEqual(800, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertIsNotNone(auction.character_url)
        self.assertEqual(0, len(auction.displayed_items))

        self.assertIsNotNone(bazaar.filters)
        self.assertIsNone(bazaar.filters.world)
        self.assertIsNone(bazaar.filters.pvp_type)
        self.assertIsNone(bazaar.filters.battleye)
        self.assertIsNone(bazaar.filters.vocation)
        self.assertIsNone(bazaar.filters.min_level)
        self.assertIsNone(bazaar.filters.max_level)
        self.assertIsNone(bazaar.filters.skill)
        self.assertIsNone(bazaar.filters.min_skill_level)
        self.assertIsNone(bazaar.filters.max_skill_level)
        self.assertEqual(AuctionOrderBy.END_DATE, bazaar.filters.order_by)
        self.assertEqual(AuctionOrder.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_from_content_current_all_filters_selected(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.page)
        self.assertEqual(2, bazaar.total_pages)
        self.assertEqual(27, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))
        self.assertIsNotNone(bazaar.url)

        auction = bazaar.entries[0]
        self.assertEqual(13448, auction.auction_id)
        self.assertEqual(150, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertIsNotNone(auction.character_url)
        self.assertEqual(4, len(auction.displayed_items))

        first_item = auction.displayed_items[0]
        self.assertEqual(1, first_item.count)
        self.assertEqual(3079, first_item.item_id)
        self.assertEqual("boots of haste", first_item.name)
        self.assertIsNotNone(first_item.image_url)

        self.assertIsNotNone(bazaar.filters)
        self.assertEqual('Antica', bazaar.filters.world)
        self.assertEqual(PvpTypeFilter.OPEN_PVP, bazaar.filters.pvp_type)
        self.assertEqual(BattlEyeTypeFilter.PROTECTED, bazaar.filters.battleye)
        self.assertEqual(VocationAuctionFilter.KNIGHT, bazaar.filters.vocation)
        self.assertEqual(1, bazaar.filters.min_level)
        self.assertEqual(1000, bazaar.filters.max_level)
        self.assertEqual(SkillFilter.MAGIC_LEVEL, bazaar.filters.skill)
        self.assertEqual(1, bazaar.filters.min_skill_level)
        self.assertEqual(5, bazaar.filters.max_skill_level)
        self.assertEqual(AuctionOrderBy.END_DATE, bazaar.filters.order_by)
        self.assertEqual(AuctionOrder.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_from_content_empty(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_CURRENT_EMPTY))
        self.assertIsNotNone(bazaar)
        self.assertFalse(bazaar.entries)

    def test_character_bazaar_from_content_history(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_HISTORY))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.page)
        self.assertEqual(777, bazaar.total_pages)
        self.assertEqual(19407, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))
        self.assertIsNotNone(bazaar.url)

        auction = bazaar.entries[0]
        self.assertEqual(1060, auction.auction_id)
        self.assertEqual(752, auction.bid)
        self.assertEqual("Maroze Loth", auction.name)
        self.assertEqual(130, auction.level)
        self.assertEqual("Pyra", auction.world)
        self.assertEqual(Vocation.ELITE_KNIGHT, auction.vocation)
        self.assertEqual(Sex.MALE, auction.sex)
        self.assertEqual(BidType.WINNING, auction.bid_type)
        self.assertIsNotNone(auction.character_url)
        self.assertEqual(2, len(auction.displayed_items))
        self.assertEqual(128, auction.outfit.outfit_id)

        first_item = auction.displayed_items[0]
        self.assertEqual(391, first_item.count)
        self.assertEqual(268, first_item.item_id)
        self.assertEqual("mana potion", first_item.name)
        self.assertIsNotNone(first_item.image_url)

        self.assertIsNone(bazaar.filters)

    def test_character_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CharacterBazaar.from_content(content)

    def test_auction_details_from_content_finished(self):
        auction = AuctionDetails.from_content(self.load_resource(FILE_AUCTION_FINISHED))

        self.assertIsNotNone(auction)

        # Listing box
        self.assertEqual("Vireloz", auction.name)
        self.assertEqual(1161, auction.level)
        self.assertEqual(Vocation.ROYAL_PALADIN, auction.vocation)
        self.assertEqual(Sex.MALE, auction.sex)
        self.assertEqual("Wintera", auction.world)
        self.assertIsNotNone(auction.outfit)
        self.assertEqual(1322, auction.outfit.outfit_id)
        self.assertEqual(4, len(auction.displayed_items))
        self.assertEqual("gnome armor", auction.displayed_items[0].name)
        self.assertEqual("falcon coif", auction.displayed_items[1].name)
        self.assertEqual("pair of soulstalkers", auction.displayed_items[2].name)
        self.assertEqual("lion spangenhelm", auction.displayed_items[3].name)

        self.assertEqual(330000, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertEqual("finished", auction.status)