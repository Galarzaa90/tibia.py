import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy.enums import AuctionBattlEyeFilter, AuctionOrderBy, AuctionOrderDirection, AuctionSearchType, \
    AuctionSkillFilter, \
    AuctionStatus, AuctionVocationFilter, BidType, PvpTypeFilter, Sex, Vocation
from tibiapy.parsers import AuctionParser, CharacterBazaarParser
from tibiapy import InvalidContentError

FILE_BAZAAR_CURRENT_EMPTY = "characterBazaar/bazaarHistoryEmpty.txt"
FILE_BAZAAR_CURRENT = "characterBazaar/bazaarCurrentAuctions.txt"
FILE_BAZAAR_CURRENT_ALL_FILTERS = "characterBazaar/bazaarCurrentAuctionsWithFilters.txt"
FILE_BAZAAR_HISTORY = "characterBazaar/bazaarHistory.txt"
FILE_AUCTION_FINISHED = "auction/auctionFinished.txt"
FILE_AUCTION_UPGRADED_ITEMS = "auction/auctionWithUpgradedItems.txt"
FILE_AUCTION_NOT_FOUND = "auction/auctionNotFound.txt"


class TestBazaar(TestCommons):
    def test_character_bazaar_parser_from_content_current_no_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT))

        self.assertIsNotNone(bazaar)

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
        self.assertEqual(AuctionOrderDirection.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_parser_from_content_current_all_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

        self.assertIsNotNone(bazaar)

        self.assertIsNotNone(bazaar.filters)
        self.assertEqual('Antica', bazaar.filters.world)
        self.assertEqual(PvpTypeFilter.OPEN_PVP, bazaar.filters.pvp_type)
        self.assertEqual(AuctionBattlEyeFilter.PROTECTED, bazaar.filters.battleye)
        self.assertEqual(AuctionVocationFilter.KNIGHT, bazaar.filters.vocation)
        self.assertEqual(1, bazaar.filters.min_level)
        self.assertEqual(1000, bazaar.filters.max_level)
        self.assertEqual(AuctionSkillFilter.MAGIC_LEVEL, bazaar.filters.skill)
        self.assertEqual(1, bazaar.filters.min_skill_level)
        self.assertEqual(50, bazaar.filters.max_skill_level)
        self.assertEqual(AuctionOrderBy.SHIELDING, bazaar.filters.order_by)
        self.assertEqual(AuctionOrderDirection.HIGHEST_LATEST, bazaar.filters.order)
        self.assertEqual(AuctionSearchType.ITEM_WILDCARD, bazaar.filters.search_type)

    def test_character_bazaar_parser_from_content_empty(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT_EMPTY))
        self.assertIsNotNone(bazaar)
        self.assertFalse(bazaar.entries)

    def test_character_bazaar_parser_from_content_history(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_HISTORY))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.current_page)
        self.assertEqual(901, bazaar.total_pages)
        self.assertEqual(22517, bazaar.results_count)
        self.assertSizeEquals(bazaar.entries, 25)
        self.assertIsNotNone(bazaar.url)

        self.assertIsNotNone(bazaar.filters)

    def test_character_bazaar_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            CharacterBazaarParser.from_content(content)

    def test_auction_parser_from_content_finished(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_FINISHED), 1297893)

        self.assertIsNotNone(auction)

        # Listing box
        self.assertEqual("Unfriendly Sanchez", auction.name)
        self.assertEqual(1_297_893, auction.auction_id)
        self.assertIn(str(auction.auction_id), auction.url)
        self.assertEqual(528, auction.level)
        self.assertEqual(Vocation.ROYAL_PALADIN, auction.vocation)
        self.assertEqual(Sex.MALE, auction.sex)
        self.assertEqual("Antica", auction.world)
        self.assertIsNotNone(auction.outfit)
        self.assertEqual(143, auction.outfit.outfit_id)
        self.assertSizeEquals(auction.displayed_items, 1)
        self.assertEqual("arrow", auction.displayed_items[0].name)

        self.assertEqual(6_000, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertEqual(AuctionStatus.FINISHED, auction.status)

        self.assertIsNotNone(auction.details)

        self.assertEqual(5_385, auction.details.hit_points)
        self.assertEqual(7_890, auction.details.mana)
        self.assertEqual(10_870, auction.details.capacity)
        self.assertEqual(637, auction.details.speed)
        self.assertEqual(0, auction.details.blessings_count)
        self.assertEqual(21, auction.details.mounts_count)
        self.assertEqual(22, auction.details.outfits_count)
        self.assertEqual(15, auction.details.titles_count)

        self.assertSizeEquals(auction.details.skills, 8)
        self.assertEqual(119, auction.details.skills_map["Distance Fighting"].level)
        self.assertEqual(83.37, auction.details.skills_map["Distance Fighting"].progress)

        self.assertIsInstance(auction.details.creation_date, datetime.datetime)
        self.assertEqual(2_426_201_303, auction.details.experience)
        self.assertEqual(157_684, auction.details.gold)
        self.assertEqual(255, auction.details.achievement_points)
        self.assertIsNotNone(auction.details.regular_world_transfer_available_date)
        self.assertEqual(446, auction.details.available_charm_points)
        self.assertEqual(3_400, auction.details.spent_charm_points)

        self.assertEqual(17, auction.details.daily_reward_streak)
        self.assertEqual(4_443, auction.details.hunting_task_points)
        self.assertEqual(0, auction.details.permanent_hunting_task_slots)
        self.assertEqual(0, auction.details.permanent_prey_slots)
        self.assertEqual(0, auction.details.hirelings)
        self.assertEqual(0, auction.details.hireling_jobs)
        self.assertEqual(0, auction.details.hireling_outfits)

        self.assertIsNotNone(auction.details.items)
        self.assertSizeEquals(auction.details.items.entries, 41)
        self.assertEqual(1, auction.details.items.total_pages)
        self.assertEqual(41, auction.details.items.results_count)
        self.assertIsNotNone(auction.details.items.get_by_name("opal"))
        self.assertIsNotNone(auction.details.items.get_by_id(5801))
        self.assertSizeEquals(auction.details.items.search('backpack'), 7)

        self.assertIsNotNone(auction.details.store_items)
        self.assertSizeEquals(auction.details.store_items.entries, 8)
        self.assertEqual(1, auction.details.store_items.total_pages)
        self.assertEqual(8, auction.details.store_items.results_count)
        self.assertIsNotNone(auction.details.store_items.get_by_name("soulfire rune"))
        self.assertIsNotNone(auction.details.store_items.get_by_id(3178))
        self.assertSizeEquals(auction.details.store_items.search('rune'), 3)

        self.assertIsNotNone(auction.details.mounts)
        self.assertSizeEquals(auction.details.mounts.entries, 20)
        self.assertEqual(1, auction.details.mounts.total_pages)
        self.assertEqual(20, auction.details.mounts.results_count)
        self.assertIsNotNone(auction.details.mounts.get_by_name("donkey"))
        self.assertIsNotNone(auction.details.mounts.get_by_id(387))
        self.assertSizeEquals(auction.details.mounts.search('war'), 2)

        self.assertIsNotNone(auction.details.store_mounts)
        self.assertSizeEquals(auction.details.store_mounts.entries, 1)
        self.assertEqual(1, auction.details.store_mounts.total_pages)
        self.assertEqual(1, auction.details.store_mounts.results_count)

        self.assertIsNotNone(auction.details.outfits)
        self.assertSizeEquals(auction.details.outfits.entries, 22)
        self.assertEqual(1, auction.details.outfits.total_pages)
        self.assertEqual(22, auction.details.outfits.results_count)

        self.assertIsNotNone(auction.details.store_outfits)
        self.assertSizeEquals(auction.details.store_outfits.entries, 0)
        self.assertEqual(1, auction.details.store_outfits.total_pages)
        self.assertEqual(0, auction.details.store_outfits.results_count)

        self.assertIsNotNone(auction.details.familiars)
        self.assertSizeEquals(auction.details.familiars.entries, 1)
        self.assertEqual(1, auction.details.familiars.total_pages)
        self.assertEqual(1, auction.details.familiars.results_count)

        self.assertSizeEquals(auction.details.blessings, 9)
        self.assertSizeEquals(auction.details.imbuements, 12)
        self.assertSizeEquals(auction.details.charms, 5)
        self.assertSizeEquals(auction.details.completed_cyclopedia_map_areas, 7)
        self.assertSizeEquals(auction.details.titles, 15)
        self.assertSizeEquals(auction.details.achievements, 100)
        self.assertSizeEquals(auction.details.bestiary_progress, 486)
        self.assertSizeEquals(auction.details.completed_bestiary_entries, 130)
        self.assertSizeEquals(auction.details.bosstiary_progress, 85)

    def test_auction_parser_from_content_finished_skip_details(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_FINISHED), skip_details=True)

        self.assertIsNotNone(auction)

        self.assertEqual("Unfriendly Sanchez", auction.name)
        self.assertIsNone(auction.details)

    def test_auction_parser_from_content_with_upgraded_items(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_UPGRADED_ITEMS))

        self.assertIsNotNone(auction)

        self.assertEqual(2, auction.displayed_items[2].tier)

    def test_auction_parser_from_content_not_found(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_NOT_FOUND))

        self.assertIsNone(auction)

    def test_auction_parser_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContentError):
            AuctionParser.from_content(content)
