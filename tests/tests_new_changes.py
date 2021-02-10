import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import Highscores, Vocation, Category, VocationFilter, Character, AccountStatus, World, WorldLocation, \
    TransferType, PvpType, ListedGuild, Guild, CharacterBazaar, BazaarType, AuctionStatus, BidType, AuctionDetails


class TestNewChanges(TestCommons, unittest.TestCase):
    def test_highscore_changes(self):
        content = self.load_resource("website_changes/1_community_highscores.txt")
        highscores = Highscores.from_content(content)

        self.assertIsNone(highscores.world)
        self.assertEqual(Category.EXPERIENCE, highscores.category)
        self.assertEqual(VocationFilter.ALL, highscores.vocation)
        self.assertEqual(1000, highscores.results_count)
        self.assertEqual(1, highscores.page)
        self.assertEqual(20, highscores.total_pages)
        first_entry = highscores.entries[0]
        self.assertEqual("Goraca", first_entry.name)
        self.assertEqual(Vocation.MASTER_SORCERER, first_entry.vocation)
        self.assertEqual(1736, first_entry.level)
        self.assertEqual(86_900_348_387, first_entry.value)

    def test_character_changes(self):
        content = self.load_resource("website_changes/2_community_characters_bobeek.txt")
        character = Character.from_content(content)

        self.assertEqual("Bobeek", character.name)
        self.assertIsNotNone(character.guild_membership)
        self.assertEqual("Hill", character.guild_membership.name)
        self.assertEqual("King", character.guild_membership.rank)
        self.assertEqual("Goraca", character.married_to)
        self.assertEqual(character.guild_name, character.guild_membership.name)
        self.assertEqual(character.guild_rank, character.guild_membership.rank)
        self.assertEqual(AccountStatus.PREMIUM_ACCOUNT, character.account_status)
        self.assertEqual(1027, character.achievement_points)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(1, character.deaths.__len__())
        self.assertEqual(character.url, Character.get_url(character.name))
        self.assertEqual(2, len(character.other_characters))
        self.assertFalse(character.hidden)

    def test_world_changes(self):
        content = self.load_resource("website_changes/3_community_world_adra.txt")
        world = World.from_content(content)

        self.assertEqual("Adra", world.name)
        self.assertEqual("Offline", world.status)
        self.assertEqual(TransferType.BLOCKED, world.transfer_type)
        self.assertEqual(PvpType.OPEN_PVP, world.pvp_type)
        self.assertEqual(WorldLocation.EUROPE, world.location)

    def test_world_guilds_changes(self):
        content = self.load_resource("website_changes/4_community_guilds_adra.txt")
        guilds = ListedGuild.list_from_content(content)

        self.assertEqual(14, len(guilds))
        guild = guilds[0]

        self.assertEqual("Bloste Solutions", guild.name)
        self.assertEqual("Adra", guild.world)
        self.assertTrue(guild.active)
        self.assertIsNone(guild.description)

    def test_guild_changes(self):
        content = self.load_resource("website_changes/5_community_guilds_world_adra_bloste+solutions.txt")
        guild = Guild.from_content(content)

        self.assertEqual("Bloste Solutions", guild.name)
        self.assertIsNone(guild.description)
        self.assertTrue(guild.open_applications)
        self.assertEqual(12, len(guild.members))
        self.assertEqual("Adra", guild.world)
        self.assertIsNone(guild.guildhall)
        leader = guild.members[0]
        self.assertEqual("Servantinho", leader.name)
        self.assertEqual("Leader", leader.rank)
        self.assertEqual(31, leader.level)
        self.assertEqual(Vocation.ELITE_KNIGHT, leader.vocation)
        self.assertIsNone(leader.title)

    def test_bazaar_current_changes(self):
        content = self.load_resource("website_changes/6_char_bazaar_current_auctions.txt")
        char_bazaar = CharacterBazaar.from_content(content)

        self.assertEqual(BazaarType.CURRENT, char_bazaar.type)
        self.assertEqual(141, char_bazaar.total_pages)
        self.assertEqual(3515, char_bazaar.results_count)
        self.assertEqual(1, char_bazaar.page)
        first_entry = char_bazaar.entries[0]
        self.assertEqual(306828, first_entry.auction_id)
        self.assertEqual("Perfect Biruley", first_entry.name)
        self.assertEqual(569, first_entry.level)
        self.assertEqual("Olera", first_entry.world)
        self.assertEqual(Vocation.KNIGHT, first_entry.vocation)
        self.assertEqual(AuctionStatus.IN_PROGRESS, first_entry.status)
        self.assertEqual(129, first_entry.outfit.outfit_id)
        self.assertEqual(14500, first_entry.bid)
        self.assertEqual(BidType.MINIMUM, first_entry.bid_type)

    def test_bazaar_auction_changes(self):
        content = self.load_resource("website_changes/7_char_bazaar_current_auctions_auctionid_312647.txt")
        auction = AuctionDetails.from_content(content)

        self.assertEqual("Lethal Nightmarez", auction.name)
        self.assertEqual(30, auction.level)
        self.assertEqual("Serdebra", auction.world)
        self.assertEqual(Vocation.KNIGHT, auction.vocation)
        self.assertEqual(AuctionStatus.IN_PROGRESS, auction.status)
        self.assertEqual(134, auction.outfit.outfit_id)
        self.assertEqual(57, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)

