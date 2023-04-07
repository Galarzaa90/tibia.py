import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import AuctionOrder, AuctionOrderBy, AuctionSearchType, AuctionStatus, BattlEyeTypeFilter, \
    BidType, \
    \
    InvalidContent, PvpTypeFilter, \
    Sex, SkillFilter, \
    Vocation, VocationAuctionFilter
from tibiapy.models import CharacterBazaar, Auction
from tibiapy.parsers.bazaar import CharacterBazaarParser, AuctionParser

FILE_BAZAAR_CURRENT_EMPTY = "bazaar/tibiacom_history_empty.txt"
FILE_BAZAAR_CURRENT = "bazaar/tibiacom_current.txt"
FILE_BAZAAR_CURRENT_ALL_FILTERS = "bazaar/tibiacom_current_all_filters.txt"
FILE_BAZAAR_HISTORY = "bazaar/tibiacom_history.txt"
FILE_AUCTION_FINISHED = "bazaar/tibiacom_auction_finished.txt"
FILE_AUCTION_UPGRADED_ITEMS = "bazaar/tibiacom_auction_upgraded_items.txt"
FILE_AUCTION_NOT_FOUND = "bazaar/tibiacom_auction_not_found.txt"


class TestBazaar(TestCommons, unittest.TestCase):
    def test_character_bazaar_from_content_current_no_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT))

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
        self.assertEqual(AuctionOrder.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_from_content_current_all_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.page)
        self.assertEqual(4, bazaar.total_pages)
        self.assertEqual(92, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))
        self.assertIsNotNone(bazaar.url)

        auction = bazaar.entries[0]
        self.assertEqual(82526, auction.auction_id)
        self.assertEqual(57000, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertIsNotNone(auction.character_url)

        self.assertIsNotNone(bazaar.filters)
        self.assertEqual('Antica', bazaar.filters.world)
        self.assertEqual(PvpTypeFilter.OPEN_PVP, bazaar.filters.pvp_type)
        self.assertEqual(BattlEyeTypeFilter.PROTECTED, bazaar.filters.battleye)
        self.assertEqual(VocationAuctionFilter.KNIGHT, bazaar.filters.vocation)
        self.assertEqual(1, bazaar.filters.min_level)
        self.assertEqual(1000, bazaar.filters.max_level)
        self.assertEqual(SkillFilter.MAGIC_LEVEL, bazaar.filters.skill)
        self.assertEqual(1, bazaar.filters.min_skill_level)
        self.assertEqual(50, bazaar.filters.max_skill_level)
        self.assertEqual(AuctionOrderBy.SHIELDING, bazaar.filters.order_by)
        self.assertEqual(AuctionOrder.HIGHEST_LATEST, bazaar.filters.order)
        self.assertEqual(AuctionSearchType.ITEM_WILDCARD, bazaar.filters.search_type)

    def test_character_bazaar_from_content_empty(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT_EMPTY))
        self.assertIsNotNone(bazaar)
        self.assertFalse(bazaar.entries)

    def test_character_bazaar_from_content_history(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_HISTORY))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.page)
        self.assertEqual(1449, bazaar.total_pages)
        self.assertEqual(36219, bazaar.results_count)
        self.assertEqual(25, len(bazaar.entries))
        self.assertIsNotNone(bazaar.url)

        auction = bazaar.entries[0]
        self.assertEqual(325058, auction.auction_id)
        self.assertEqual(900, auction.bid)
        self.assertEqual("Rcrazy Illuminati", auction.name)
        self.assertEqual(255, auction.level)
        self.assertEqual("Celebra", auction.world)
        self.assertEqual(Vocation.MASTER_SORCERER, auction.vocation)
        self.assertEqual(Sex.MALE, auction.sex)
        self.assertEqual(BidType.WINNING, auction.bid_type)
        self.assertIsNotNone(auction.character_url)
        self.assertEqual(1, len(auction.displayed_items))
        self.assertEqual(143, auction.outfit.outfit_id)

        first_item = auction.displayed_items[0]
        self.assertEqual(1, first_item.count)
        self.assertEqual(25700, first_item.item_id)
        self.assertEqual("dream blossom staff", first_item.name)
        self.assertIsNotNone(first_item.image_url)

        self.assertIsNone(bazaar.filters)

    def test_character_bazaar_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CharacterBazaarParser.from_content(content)

    def test_auction_details_from_content_finished(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_FINISHED))

        self.assertIsNotNone(auction)

        # Listing box
        self.assertEqual("Hikeezor", auction.name)
        self.assertIn(auction.name, auction.character_url)
        self.assertIn(str(auction.auction_id), auction.url)
        self.assertEqual(1496, auction.level)
        self.assertEqual(Vocation.ELDER_DRUID, auction.vocation)
        self.assertEqual(Sex.MALE, auction.sex)
        self.assertEqual("Astera", auction.world)
        self.assertIsNotNone(auction.outfit)
        self.assertEqual(130, auction.outfit.outfit_id)
        self.assertEqual(2, len(auction.displayed_items))
        self.assertEqual("lasting exercise rod", auction.displayed_items[0].name)
        self.assertEqual("lasting exercise wand", auction.displayed_items[1].name)

        self.assertEqual(230000, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)
        self.assertEqual(AuctionStatus.FINISHED, auction.status)

        self.assertEqual(7625, auction.hit_points)
        self.assertEqual(44730, auction.mana)
        self.assertEqual(15350, auction.capacity)
        self.assertEqual(1605, auction.speed)
        self.assertEqual(0, auction.blessings_count)
        self.assertEqual(65, auction.mounts_count)
        self.assertEqual(51, auction.outfits_count)
        self.assertEqual(36, auction.titles_count)

        self.assertEqual(8, len(auction.skills))
        self.assertEqual(21, auction.skills_map["Distance Fighting"].level)
        self.assertEqual(16.37, auction.skills_map["Distance Fighting"].progress)

        self.assertIsInstance(auction.creation_date, datetime.datetime)
        self.assertEqual(55611897119, auction.experience)
        self.assertEqual(1000, auction.gold)
        self.assertEqual(1147, auction.achievement_points)
        self.assertIsNone(auction.regular_world_transfer_available_date)
        self.assertEqual(5110, auction.available_charm_points)
        self.assertEqual(13600, auction.spent_charm_points)

        self.assertEqual(935, auction.daily_reward_streak)
        self.assertEqual(64304, auction.hunting_task_points)
        self.assertEqual(1, auction.permanent_hunting_task_slots)
        self.assertEqual(1, auction.permanent_prey_slots)
        self.assertEqual(2, auction.hirelings)
        self.assertEqual(4, auction.hireling_jobs)
        self.assertEqual(1, auction.hireling_outfits)

        self.assertIsNotNone(auction.items)
        self.assertEqual(5, len(auction.items.entries))
        self.assertEqual(1, auction.items.total_pages)
        self.assertEqual(5, auction.items.results)
        # self.assertEqual(141, auction.items.get_by_name("label").item_id)
        # self.assertEqual("cigar", auction.items.get_by_id(141).name)
        # self.assertEqual(7, len(auction.items.search('backpack')))

        self.assertIsNotNone(auction.store_items)
        self.assertEqual(30, len(auction.store_items.entries))
        self.assertEqual(1, auction.store_items.total_pages)
        self.assertEqual(30, auction.store_items.results)
        # self.assertEqual(23721, auction.store_items.get_by_name("gold pouch").item_id)
        # self.assertEqual("gold pouch", auction.store_items.get_by_id(23721).name)
        # self.assertEqual(2, len(auction.store_items.search('rune')))

        self.assertIsNotNone(auction.mounts)
        self.assertEqual(30, len(auction.mounts.entries))
        self.assertEqual(3, auction.mounts.total_pages)
        self.assertEqual(61, auction.mounts.results)
        # self.assertEqual(387, auction.mounts.get_by_name("donkey").mount_id)
        # self.assertEqual("Donkey", auction.mounts.get_by_id(387).name)
        # self.assertEqual(1, len(auction.mounts.search('drag')))

        self.assertIsNotNone(auction.store_mounts)
        self.assertEqual(4, len(auction.store_mounts.entries))
        self.assertEqual(1, auction.store_mounts.total_pages)
        self.assertEqual(4, auction.store_mounts.results)
        # self.assertEqual(906, auction.store_mounts.get_by_name("Wolpertinger").mount_id)
        # self.assertEqual("Wolpertinger", auction.store_mounts.get_by_id(906).name)
        # self.assertEqual(1, len(auction.store_mounts.search('Wolpertinger')))

        self.assertIsNotNone(auction.outfits)
        self.assertEqual(30, len(auction.outfits.entries))
        self.assertEqual(2, auction.outfits.total_pages)
        self.assertEqual(50, auction.outfits.results)
        # self.assertEqual(151, auction.outfits.get_by_name("pirate").outfit_id)
        # self.assertEqual('Glooth Engineer', auction.outfits.get_by_id(610).name)
        # self.assertEqual(2, len(auction.outfits.search('demon')))

        self.assertIsNotNone(auction.store_outfits)
        self.assertEqual(1, len(auction.store_outfits.entries))
        self.assertEqual(1, auction.store_outfits.total_pages)
        self.assertEqual(1, auction.store_outfits.results)
        # self.assertEqual(962, auction.store_outfits.get_by_name("retro warrior").outfit_id)
        # self.assertEqual('Retro Warrior', auction.store_outfits.get_by_id(962).name)
        # self.assertEqual(2, len(auction.store_outfits.search('retro')))

        self.assertIsNotNone(auction.familiars)
        self.assertEqual(2, len(auction.familiars.entries))
        self.assertEqual(1, auction.familiars.total_pages)
        self.assertEqual(2, auction.familiars.results)
        # self.assertEqual(992, auction.familiars.get_by_name("emberwing").familiar_id)
        # self.assertEqual('Emberwing', auction.familiars.get_by_id(992).name)
        # self.assertEqual(1, len(auction.familiars.search('ember')))

        self.assertEqual(9, len(auction.blessings))
        self.assertEqual(23, len(auction.imbuements))
        self.assertEqual(15, len(auction.charms))
        self.assertEqual(19, len(auction.completed_cyclopedia_map_areas))
        self.assertEqual(36, len(auction.titles))
        self.assertEqual(451, len(auction.achievements))
        self.assertEqual(702, len(auction.bestiary_progress))
        self.assertEqual(637, len(auction.completed_bestiary_entries))

    def _test_auction_details_from_content_finished_skip_details(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_FINISHED), skip_details=True)

        self.assertIsNotNone(auction)

        # Listing box
        self.assertEqual("Vireloz", auction.name)
        self.assertIn(auction.name, auction.character_url)
        self.assertIn(str(auction.auction_id), auction.url)
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
        self.assertEqual(AuctionStatus.FINISHED, auction.status)

    def _test_auction_details_from_content_with_upgraded_items(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_UPGRADED_ITEMS))

        self.assertIsNotNone(auction)

        self.assertEqual(1, auction.displayed_items[0].tier)
        self.assertEqual(1, auction.items.entries[1].tier)


    def test_auction_details_from_content_not_found(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_NOT_FOUND))

        self.assertIsNone(auction)

    def test_auction_details_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            AuctionParser.from_content(content)