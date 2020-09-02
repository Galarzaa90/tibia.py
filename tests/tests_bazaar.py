import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import AuctionOrder, AuctionOrderBy, BattlEyeTypeFilter, BidType, CharacterBazaar, PvpTypeFilter, \
    SkillFilter, \
    VocationAuctionFilter

FILE_BAZAAR_CURRENT_ALL_FILTERS = "auctions/tibiacom_current_all_filters.txt"


class TestBazaar(TestCommons, unittest.TestCase):
    def test_character_bazaar_from_content_all_filters_selected(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.page)
        self.assertEqual(2, bazaar.total_pages)
        self.assertEqual(27, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))

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