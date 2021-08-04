import unittest

from tests.tests_tibiapy import TestCommons
from tibiapy import GuildsSection, Highscores, KillStatistics, Vocation, Category, VocationFilter, Character, \
    AccountStatus, World, \
    WorldLocation, \
    TransferType, PvpType, GuildEntry, Guild, CharacterBazaar, BazaarType, AuctionStatus, BidType, Auction


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
        self.assertEqual(1904, first_entry.level)
        self.assertEqual(114_797_203_877, first_entry.value)

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
        self.assertEqual(1038, character.achievement_points)
        self.assertIsNone(character.deletion_date)
        self.assertIsNotNone(character.deaths)
        self.assertEqual(1, character.deaths.__len__())
        self.assertEqual(character.url, Character.get_url(character.name))
        self.assertEqual(3, len(character.other_characters))
        self.assertFalse(character.hidden)

    def test_world_changes(self):
        content = self.load_resource("website_changes/3_community_world_adra.txt")
        world = World.from_content(content)

        self.assertEqual("Adra", world.name)
        self.assertEqual("Online", world.status)
        self.assertEqual(TransferType.BLOCKED, world.transfer_type)
        self.assertEqual(PvpType.OPEN_PVP, world.pvp_type)
        self.assertEqual(WorldLocation.EUROPE, world.location)

    def test_world_guilds_changes(self):
        content = self.load_resource("website_changes/4_community_guilds_adra.txt")
        guilds_section = GuildsSection.from_content(content)

        guilds = guilds_section.entries
        self.assertEqual(12, len(guilds))
        guild = guilds[0]

        self.assertEqual("Ambassadors", guild.name)
        self.assertEqual("Adra", guild.world)
        self.assertTrue(guild.active)

    def test_guild_changes(self):
        content = self.load_resource("website_changes/5_community_guilds_world_adra_ambassadors.txt")
        guild = Guild.from_content(content)

        self.assertEqual("Ambassadors", guild.name)
        self.assertTrue(guild.open_applications)
        self.assertEqual(31, len(guild.members))
        self.assertEqual("Adra", guild.world)
        self.assertIsNone(guild.guildhall)
        leader = guild.members[0]
        self.assertEqual("Emsky Ed", leader.name)
        self.assertEqual("Leader", leader.rank)
        self.assertEqual(293, leader.level)
        self.assertEqual(Vocation.ELDER_DRUID, leader.vocation)
        self.assertIsNone(leader.title)

    def test_bazaar_current_changes(self):
        content = self.load_resource("website_changes/6_char_bazaar_current_auctions.txt")
        char_bazaar = CharacterBazaar.from_content(content)

        self.assertEqual(BazaarType.CURRENT, char_bazaar.type)
        self.assertEqual(94, char_bazaar.total_pages)
        self.assertEqual(2339, char_bazaar.results_count)
        self.assertEqual(1, char_bazaar.page)
        first_entry = char_bazaar.entries[0]
        self.assertEqual(564217, first_entry.auction_id)
        self.assertEqual("Quaak", first_entry.name)
        self.assertEqual(664, first_entry.level)
        self.assertEqual("Estela", first_entry.world)
        self.assertEqual(Vocation.ROYAL_PALADIN, first_entry.vocation)
        self.assertEqual(AuctionStatus.IN_PROGRESS, first_entry.status)
        self.assertEqual(128, first_entry.outfit.outfit_id)
        self.assertEqual(17000, first_entry.bid)
        self.assertEqual(BidType.MINIMUM, first_entry.bid_type)

    def test_bazaar_auction_changes(self):
        content = self.load_resource("website_changes/7_char_bazaar_current_auctions_auctionid_549159.txt")
        auction = Auction.from_content(content)

        self.assertEqual("Knight Sparkizyn", auction.name)
        self.assertEqual(363, auction.level)
        self.assertEqual("Quelibra", auction.world)
        self.assertEqual(Vocation.KNIGHT, auction.vocation)
        self.assertEqual(AuctionStatus.IN_PROGRESS, auction.status)
        self.assertEqual(129, auction.outfit.outfit_id)
        self.assertEqual(3801, auction.bid)
        self.assertEqual(BidType.MINIMUM, auction.bid_type)

    def test_killstatistics_changes(self):
        content = self.load_resource("website_changes/8_community_kill_statistics_world_adra.txt")
        kill_statistics = KillStatistics.from_content(content)

        self.assertIsInstance(kill_statistics, KillStatistics)
        self.assertEqual(kill_statistics.world, "Adra")
        self.assertEqual(len(kill_statistics.entries), 784)

        # players shortcurt property
        self.assertEqual(kill_statistics.players, kill_statistics.entries["players"])
        self.assertEqual(kill_statistics.players.last_day_killed, 3)
        self.assertEqual(kill_statistics.players.last_day_killed, kill_statistics.players.last_day_players_killed)
        self.assertEqual(kill_statistics.players.last_week_killed, 76)
        self.assertEqual(kill_statistics.players.last_week_killed, kill_statistics.players.last_week_players_killed)

        # demons
        demons_entry = kill_statistics.entries["demons"]
        self.assertEqual(84, demons_entry.last_day_killed)
        self.assertEqual(1, demons_entry.last_day_players_killed)
        self.assertEqual(1439, demons_entry.last_week_killed)
        self.assertEqual(1, demons_entry.last_week_players_killed)

