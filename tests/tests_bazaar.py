import datetime

from tests.tests_tibiapy import TestCommons
from tibiapy import AuctionOrderDirection, AuctionOrderBy, AuctionSearchType, AuctionStatus, AuctionBattlEyeFilter, \
    BidType, \
 \
    InvalidContent, PvpTypeFilter, \
    Sex, AuctionSkillFilter, \
    Vocation, AuctionVocationFilter
from tibiapy.parsers.bazaar import CharacterBazaarParser, AuctionParser

FILE_BAZAAR_CURRENT_EMPTY = "bazaar/bazaarHistoryEmpty.txt"
FILE_BAZAAR_CURRENT = "bazaar/bazaarCurrentAuctions.txt"
FILE_BAZAAR_CURRENT_ALL_FILTERS = "bazaar/bazaarCurrentAuctionsWithFilters.txt"
FILE_BAZAAR_HISTORY = "bazaar/bazaarHistory.txt"
FILE_AUCTION_FINISHED = "bazaar/auctionFinished.txt"
FILE_AUCTION_UPGRADED_ITEMS = "bazaar/auctionWithUpgradedItems.txt"
FILE_AUCTION_NOT_FOUND = "bazaar/auctionNotFound.txt"


class TestBazaar(TestCommons):
    def test_character_bazaar_parser_from_content_current_no_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT))

        self.assertIsNotNone(bazaar)
        self.assertEqual(300, bazaar.current_page)
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
        self.assertEqual(AuctionOrderDirection.LOWEST_EARLIEST, bazaar.filters.order)

    def test_character_bazaar_parser_from_content_current_all_filters_selected(self):
        bazaar = CharacterBazaarParser.from_content(self.load_resource(FILE_BAZAAR_CURRENT_ALL_FILTERS))

        self.assertIsNotNone(bazaar)
        self.assertEqual(1, bazaar.current_page)
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

    def test_character_bazaar_parser_from_content_unrelated(self):
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

        self.assertEqual(7625, auction.details.hit_points)
        self.assertEqual(44730, auction.details.mana)
        self.assertEqual(15350, auction.details.capacity)
        self.assertEqual(1605, auction.details.speed)
        self.assertEqual(0, auction.details.blessings_count)
        self.assertEqual(65, auction.details.mounts_count)
        self.assertEqual(51, auction.details.outfits_count)
        self.assertEqual(36, auction.details.titles_count)

        self.assertEqual(8, len(auction.details.skills))
        self.assertEqual(21, auction.details.skills_map["Distance Fighting"].level)
        self.assertEqual(16.37, auction.details.skills_map["Distance Fighting"].progress)

        self.assertIsInstance(auction.details.creation_date, datetime.datetime)
        self.assertEqual(55611897119, auction.details.experience)
        self.assertEqual(1000, auction.details.gold)
        self.assertEqual(1147, auction.details.achievement_points)
        self.assertIsNone(auction.details.regular_world_transfer_available_date)
        self.assertEqual(5110, auction.details.available_charm_points)
        self.assertEqual(13600, auction.details.spent_charm_points)

        self.assertEqual(935, auction.details.daily_reward_streak)
        self.assertEqual(64304, auction.details.hunting_task_points)
        self.assertEqual(1, auction.details.permanent_hunting_task_slots)
        self.assertEqual(1, auction.details.permanent_prey_slots)
        self.assertEqual(2, auction.details.hirelings)
        self.assertEqual(4, auction.details.hireling_jobs)
        self.assertEqual(1, auction.details.hireling_outfits)

        self.assertIsNotNone(auction.details.items)
        self.assertEqual(5, len(auction.details.items.entries))
        self.assertEqual(1, auction.details.items.total_pages)
        self.assertEqual(5, auction.details.items.results_count)
        self.assertEqual(3507, auction.details.items.get_by_name("label").item_id)
        self.assertEqual("brocade backpack", auction.details.items.get_by_id(8860).name)
        self.assertEqual(1, len(auction.details.items.search('parcel')))

        self.assertIsNotNone(auction.details.store_items)
        self.assertEqual(30, len(auction.details.store_items.entries))
        self.assertEqual(1, auction.details.store_items.total_pages)
        self.assertEqual(30, auction.details.store_items.results_count)
        self.assertEqual(32917, auction.details.store_items.get_by_name("gold deed").item_id)
        self.assertEqual("podium of vigour", auction.details.store_items.get_by_id(38707).name)
        self.assertEqual(5, len(auction.details.store_items.search('plushie')))

        self.assertIsNotNone(auction.details.mounts)
        self.assertEqual(30, len(auction.details.mounts.entries))
        self.assertEqual(3, auction.details.mounts.total_pages)
        self.assertEqual(61, auction.details.mounts.results_count)
        self.assertEqual(387, auction.details.mounts.get_by_name("donkey").mount_id)
        self.assertEqual("Donkey", auction.details.mounts.get_by_id(387).name)
        self.assertEqual(1, len(auction.details.mounts.search('drag')))

        self.assertIsNotNone(auction.details.store_mounts)
        self.assertEqual(4, len(auction.details.store_mounts.entries))
        self.assertEqual(1, auction.details.store_mounts.total_pages)
        self.assertEqual(4, auction.details.store_mounts.results_count)
        self.assertEqual(427, auction.details.store_mounts.get_by_name("shadow draptor").mount_id)
        self.assertEqual("Shadow Draptor", auction.details.store_mounts.get_by_id(427).name)
        self.assertEqual(1, len(auction.details.store_mounts.search('shadow')))

        self.assertIsNotNone(auction.details.outfits)
        self.assertEqual(30, len(auction.details.outfits.entries))
        self.assertEqual(2, auction.details.outfits.total_pages)
        self.assertEqual(50, auction.details.outfits.results_count)
        self.assertEqual(153, auction.details.outfits.get_by_name("beggar").outfit_id)
        self.assertEqual('Beggar', auction.details.outfits.get_by_id(153).name)
        self.assertEqual(2, len(auction.details.outfits.search('demon')))

        self.assertIsNotNone(auction.details.store_outfits)
        self.assertEqual(1, len(auction.details.store_outfits.entries))
        self.assertEqual(1, auction.details.store_outfits.total_pages)
        self.assertEqual(1, auction.details.store_outfits.results_count)
        self.assertEqual(1202, auction.details.store_outfits.get_by_name("void master").outfit_id)
        self.assertEqual('Void Master', auction.details.store_outfits.get_by_id(1202).name)
        self.assertEqual(1, len(auction.details.store_outfits.search('void')))

        self.assertIsNotNone(auction.details.familiars)
        self.assertEqual(2, len(auction.details.familiars.entries))
        self.assertEqual(1, auction.details.familiars.total_pages)
        self.assertEqual(2, auction.details.familiars.results_count)
        self.assertEqual(993, auction.details.familiars.get_by_name("grovebeast").familiar_id)
        self.assertEqual('Grovebeast', auction.details.familiars.get_by_id(993).name)
        self.assertEqual(1, len(auction.details.familiars.search('grove')))

        self.assertEqual(9, len(auction.details.blessings))
        self.assertEqual(23, len(auction.details.imbuements))
        self.assertEqual(15, len(auction.details.charms))
        self.assertEqual(19, len(auction.details.completed_cyclopedia_map_areas))
        self.assertEqual(36, len(auction.details.titles))
        self.assertEqual(451, len(auction.details.achievements))
        self.assertEqual(702, len(auction.details.bestiary_progress))
        self.assertEqual(637, len(auction.details.completed_bestiary_entries))

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

    def test_auction_details_from_content_with_upgraded_items(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_UPGRADED_ITEMS))

        self.assertIsNotNone(auction)

        self.assertEqual(1, auction.displayed_items[0].tier)
        self.assertEqual(1, auction.details.items.entries[1].tier)


    def test_auction_details_from_content_not_found(self):
        auction = AuctionParser.from_content(self.load_resource(FILE_AUCTION_NOT_FOUND))

        self.assertIsNone(auction)

    def test_auction_details_from_content_unrelated(self):
        """Testing parsing an unrelated tibia.com section"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        with self.assertRaises(InvalidContent):
            AuctionParser.from_content(content)
