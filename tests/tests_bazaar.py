import datetime
import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import AuctionDetails, AuctionOrder, AuctionOrderBy, AuctionSearchType, AuctionStatus, BattlEyeTypeFilter, \
    BidType, \
    CharacterBazaar, \
    InvalidContent, PvpTypeFilter, \
    Sex, SkillFilter, \
    Vocation, VocationAuctionFilter

FILE_BAZAAR_CURRENT_EMPTY = "bazaar/tibiacom_history_empty.txt"
FILE_BAZAAR_CURRENT = "bazaar/tibiacom_current.txt"
FILE_BAZAAR_CURRENT_ALL_FILTERS = "bazaar/tibiacom_current_all_filters.txt"
FILE_BAZAAR_HISTORY = "bazaar/tibiacom_history.txt"
FILE_AUCTION_FINISHED = "bazaar/tibiacom_auction_finished.txt"
FILE_AUCTION_NOT_FOUND = "bazaar/tibiacom_auction_not_found.txt"


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
        self.assertEqual(AuctionOrder.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_from_content_current_all_filters_selected(self):
        bazaar = CharacterBazaar.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

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
        self.assertEqual("potion", bazaar.filters.item)
        self.assertEqual(AuctionSearchType.ITEM_WILDCARD, bazaar.filters.search_type)

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

    def test_character_bazaar_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            CharacterBazaar.from_content(content)

    def test_auction_details_from_content_finished(self):
        auction = AuctionDetails.from_content(self.load_resource(FILE_AUCTION_FINISHED))

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

        self.assertEqual(11715, auction.hit_points)
        self.assertEqual(17385, auction.mana)
        self.assertEqual(23530, auction.capacity)
        self.assertEqual(1270, auction.speed)
        self.assertEqual(0, auction.blessings_count)
        self.assertEqual(23, auction.mounts_count)
        self.assertEqual(35, auction.outfits_count)
        self.assertEqual(16, auction.titles_count)

        self.assertEqual(8, len(auction.skills))
        self.assertEqual(128, auction.skills_map["Distance Fighting"].level)
        self.assertEqual(11.43, auction.skills_map["Distance Fighting"].progress)

        self.assertIsInstance(auction.creation_date, datetime.datetime)
        self.assertEqual(26006721711, auction.experience)
        self.assertEqual(41893, auction.gold)
        self.assertEqual(540, auction.achievement_points)
        self.assertIsInstance(auction.regular_world_transfer_available_date, datetime.datetime)
        self.assertEqual(110, auction.available_charm_points)
        self.assertEqual(5800, auction.spent_charm_points)

        self.assertEqual(2, auction.daily_reward_streak)
        self.assertEqual(1494, auction.hunting_task_points)
        self.assertEqual(0, auction.permanent_hunting_task_slots)
        self.assertEqual(1, auction.permanent_prey_slots)
        self.assertEqual(1, auction.hirelings)
        self.assertEqual(3, auction.hireling_jobs)
        self.assertEqual(0, auction.hireling_outfits)

        self.assertIsNotNone(auction.items)
        self.assertEqual(76, len(auction.items.entries))
        self.assertEqual(8, auction.items.total_pages)
        self.assertEqual(567, auction.items.results)
        self.assertEqual(141, auction.items.get_by_name("cigar").item_id)
        self.assertEqual("cigar", auction.items.get_by_id(141).name)
        self.assertEqual(7, len(auction.items.search('backpack')))

        self.assertIsNotNone(auction.store_items)
        self.assertEqual(16, len(auction.store_items.entries))
        self.assertEqual(1, auction.store_items.total_pages)
        self.assertEqual(16, auction.store_items.results)
        self.assertEqual(23721, auction.store_items.get_by_name("gold pouch").item_id)
        self.assertEqual("gold pouch", auction.store_items.get_by_id(23721).name)
        self.assertEqual(2, len(auction.store_items.search('rune')))

        self.assertIsNotNone(auction.mounts)
        self.assertEqual(22, len(auction.mounts.entries))
        self.assertEqual(1, auction.mounts.total_pages)
        self.assertEqual(22, auction.mounts.results)
        self.assertEqual(387, auction.mounts.get_by_name("donkey").mount_id)
        self.assertEqual("Donkey", auction.mounts.get_by_id(387).name)
        self.assertEqual(1, len(auction.mounts.search('drag')))

        self.assertIsNotNone(auction.store_mounts)
        self.assertEqual(1, len(auction.store_mounts.entries))
        self.assertEqual(1, auction.store_mounts.total_pages)
        self.assertEqual(1, auction.store_mounts.results)
        self.assertEqual(906, auction.store_mounts.get_by_name("Wolpertinger").mount_id)
        self.assertEqual("Wolpertinger", auction.store_mounts.get_by_id(906).name)
        self.assertEqual(1, len(auction.store_mounts.search('Wolpertinger')))

        self.assertIsNotNone(auction.outfits)
        self.assertEqual(30, len(auction.outfits.entries))
        self.assertEqual(2, auction.outfits.total_pages)
        self.assertEqual(33, auction.outfits.results)
        self.assertEqual(151, auction.outfits.get_by_name("pirate").outfit_id)
        self.assertEqual('Glooth Engineer', auction.outfits.get_by_id(610).name)
        self.assertEqual(2, len(auction.outfits.search('demon')))

        self.assertIsNotNone(auction.store_outfits)
        self.assertEqual(2, len(auction.store_outfits.entries))
        self.assertEqual(1, auction.store_outfits.total_pages)
        self.assertEqual(2, auction.store_outfits.results)
        self.assertEqual(962, auction.store_outfits.get_by_name("retro warrior").outfit_id)
        self.assertEqual('Retro Warrior', auction.store_outfits.get_by_id(962).name)
        self.assertEqual(2, len(auction.store_outfits.search('retro')))

        self.assertEqual(9, len(auction.blessings))
        self.assertEqual(18, len(auction.imbuements))
        self.assertEqual(8, len(auction.charms))
        self.assertEqual(0, len(auction.completed_cyclopedia_map_areas))
        self.assertEqual(16, len(auction.titles))
        self.assertEqual(214, len(auction.achievements))
        self.assertEqual(509, len(auction.bestiary_progress))
        self.assertEqual(205, len(auction.completed_bestiary_entries))

    def test_auction_details_from_content_finished_skip_details(self):
        auction = AuctionDetails.from_content(self.load_resource(FILE_AUCTION_FINISHED), skip_details=True)

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

    def test_auction_details_from_content_not_found(self):
        auction = AuctionDetails.from_content(self.load_resource(FILE_AUCTION_NOT_FOUND))

        self.assertIsNone(auction)

    def test_auction_details_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            AuctionDetails.from_content(content)