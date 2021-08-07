import datetime
import sys
import unittest.mock

import aiohttp
import asynctest
from aioresponses import aioresponses

import tibiapy
from tests.tests_bazaar import FILE_BAZAAR_CURRENT, FILE_BAZAAR_HISTORY, FILE_AUCTION_FINISHED
from tests.tests_character import FILE_CHARACTER_RESOURCE, FILE_CHARACTER_NOT_FOUND
from tests.tests_events import FILE_EVENT_CALENDAR
from tests.tests_forums import FILE_BOARD_THREAD_LIST, FILE_CM_POST_ARCHIVE_PAGES, FILE_WORLD_BOARDS
from tests.tests_guild import FILE_GUILD_FULL, FILE_GUILD_LIST
from tests.tests_highscores import FILE_HIGHSCORES_FULL
from tests.tests_house import FILE_HOUSE_FULL, FILE_HOUSE_LIST
from tests.tests_kill_statistics import FILE_KILL_STATISTICS_FULL
from tests.tests_leaderboards import FILE_LEADERBOARD_CURRENT
from tests.tests_news import FILE_NEWS_LIST, FILE_NEWS_ARTICLE
from tests.tests_tibiapy import TestCommons
from tests.tests_world import FILE_WORLD_FULL, FILE_WORLD_LIST
from tibiapy import BoardEntry, CharacterBazaar, Client, Character, CMPostArchive, ForumBoard, Guild, GuildsSection, \
    Highscores, \
    HouseType, \
    HousesSection, \
    Leaderboard, NewsArchive, VocationFilter, \
    Category, \
    House, HouseEntry, \
    GuildEntry, \
    KillStatistics, NewsEntry, News, World, WorldOverview, Forbidden, NetworkError, CreatureEntry, Auction, \
    EventSchedule


class TestClient(asynctest.TestCase, TestCommons):
    def setUp(self):
        self.client = Client()

    async def tearDown(self):
        await self.client.session.close()

    async def test_client_init_pass_session(self):
        """Testing creating an instance passing a session"""
        headers = {"User-Agent": "Python Unit Test"}
        session = aiohttp.ClientSession(headers=headers)
        client = Client(session=session)

        self.assertEqual(client.session._default_headers, headers)

        await client.session.close()

    @aioresponses()
    async def test_client_handle_errors(self, mock):
        """Testing error handling"""
        mock.get(WorldOverview.get_url(), status=403)
        with self.assertRaises(Forbidden):
            await self.client.fetch_world_list()

        mock.get(WorldOverview.get_url(), status=404)
        with self.assertRaises(NetworkError):
            await self.client.fetch_world_list()

        mock.get(NewsEntry.get_list_url(), exception=aiohttp.ClientError())
        with self.assertRaises(NetworkError):
            await self.client.fetch_world_list()

        mock.post(NewsEntry.get_list_url(), exception=aiohttp.ClientOSError())
        with self.assertRaises(NetworkError):
            await self.client.fetch_recent_news(30)

    @aioresponses()
    async def test_client_fetch_character(self, mock):
        """Testing fetching a character"""
        name = "Tschas"
        content = self.load_resource(FILE_CHARACTER_RESOURCE)
        mock.get(Character.get_url(name), status=200, body=content)
        character = await self.client.fetch_character(name)

        self.assertIsInstance(character.data, Character)

    @aioresponses()
    async def test_client_fetch_character_not_found(self, mock):
        """Testing fetching a non existent character"""
        name = "Nezune"
        content = self.load_resource(FILE_CHARACTER_NOT_FOUND)
        mock.get(Character.get_url(name), status=200, body=content)
        character = await self.client.fetch_character(name)

        self.assertIsNone(character.data)

    @aioresponses()
    async def test_client_fetch_guild(self, mock):
        """Testing fetching a guild"""
        name = "Vitam et Mortem"
        content = self.load_resource(FILE_GUILD_FULL)
        mock.get(Guild.get_url(name), status=200, body=content)
        guild = await self.client.fetch_guild(name)

        self.assertIsInstance(guild.data, Guild)

    @aioresponses()
    async def test_client_fetch_world_guilds(self, mock):
        """Testing fetching a world's guild list"""
        world = "Zuna"
        content = self.load_resource(FILE_GUILD_LIST)
        mock.get(GuildsSection.get_url(world), status=200, body=content)
        response = await self.client.fetch_world_guilds(world)
        guilds = response.data.entries

        self.assertIsInstance(guilds[0], GuildEntry)

    @aioresponses()
    async def test_client_fetch_highscores_page(self, mock):
        """Testing fetching a highscores page"""
        world = "Estela"
        category = Category.MAGIC_LEVEL
        vocations = VocationFilter.KNIGHTS
        content = self.load_resource(FILE_HIGHSCORES_FULL)
        mock.get(Highscores.get_url(world, category, vocations), status=200, body=content)
        highscores = await self.client.fetch_highscores_page(world, category, vocations)

        self.assertIsInstance(highscores.data, Highscores)

    @aioresponses()
    async def test_client_fetch_house(self, mock):
        """Testing fetching a house"""
        world = "Antica"
        house_id = 5236
        content = self.load_resource(FILE_HOUSE_FULL)
        mock.get(House.get_url(house_id, world), status=200, body=content)
        house = await self.client.fetch_house(house_id, world)

        self.assertIsInstance(house.data, House)

    @aioresponses()
    async def test_client_fetch_world_houses(self, mock):
        """Testing fetching a world's houses"""
        world = "Antica"
        city = "Edron"
        content = self.load_resource(FILE_HOUSE_LIST)
        mock.get(HousesSection.get_url(world=world, town=city, house_type=HouseType.HOUSE), status=200, body=content)
        houses = await self.client.fetch_world_houses(world, city)

        self.assertIsInstance(houses.data, HousesSection)
        self.assertIsInstance(houses.data.entries[0], HouseEntry)

    @aioresponses()
    async def test_client_fetch_kill_statistics(self, mock):
        """Testing fetching kill statistics"""
        world = "Antica"
        content = self.load_resource(FILE_KILL_STATISTICS_FULL)
        mock.get(KillStatistics.get_url(world), status=200, body=content)
        kill_statistics = await self.client.fetch_kill_statistics(world)

        self.assertIsInstance(kill_statistics.data, KillStatistics)

    @aioresponses()
    async def test_client_fetch_recent_news(self, mock):
        """Testing fetching recent nows"""
        content = self.load_resource(FILE_NEWS_LIST)
        mock.post(NewsArchive.get_url(), status=200, body=content)
        recent_news = await self.client.fetch_recent_news(30)

        self.assertIsInstance(recent_news.data, NewsArchive)
        self.assertIsInstance(recent_news.data.entries[0], NewsEntry)

    async def test_client_fetch_news_archive_invalid_dates(self):
        """Testing fetching news archive with invalid dates"""
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        with self.assertRaises(ValueError):
            await self.client.fetch_news_archive(today, yesterday)

    @aioresponses()
    async def test_client_fetch_news(self, mock):
        """Testing fetch news"""
        news_id = 6000
        content = self.load_resource(FILE_NEWS_ARTICLE)
        mock.get(News.get_url(news_id), status=200, body=content)
        news = await self.client.fetch_news(news_id)

        self.assertIsInstance(news.data, News)

    @aioresponses()
    async def test_client_fetch_world(self, mock):
        """Testing fetching a world"""
        name = "Antica"
        content = self.load_resource(FILE_WORLD_FULL)
        mock.get(World.get_url(name), status=200, body=content)
        world = await self.client.fetch_world(name)

        self.assertIsInstance(world.data, World)

    @aioresponses()
    async def test_client_fetch_world_list(self, mock):
        """Testing fetching the world list"""
        content = self.load_resource(FILE_WORLD_LIST)
        mock.get(WorldOverview.get_url(), status=200, body=content)
        worlds = await self.client.fetch_world_list()

        self.assertIsInstance(worlds.data, WorldOverview)

    @aioresponses()
    async def test_client_fetch_boosted_creature(self, mock):
        """Testing fetching the boosted creature"""
        content = self.load_resource(self.FILE_UNRELATED_SECTION)
        mock.get(News.get_list_url(), status=200, body=content)
        creature = await self.client.fetch_boosted_creature()

        self.assertIsInstance(creature.data, CreatureEntry)

    @aioresponses()
    async def test_client_fetch_cm_post_archive(self, mock):
        """Testing fetching the CM Post Archive"""
        content = self.load_resource(FILE_CM_POST_ARCHIVE_PAGES)
        start_date = datetime.date.today()-datetime.timedelta(days=40)
        end_date = datetime.date.today()
        mock.get(CMPostArchive.get_url(start_date, end_date), status=200, body=content)
        cm_post_archive = await self.client.fetch_cm_post_archive(start_date, end_date)

        self.assertIsInstance(cm_post_archive.data, CMPostArchive)

    async def test_client_fetch_cm_post_archive_invalid_dates(self):
        """Testing fetching the CM Post Archive with invalid dates"""
        end_date = datetime.date.today()-datetime.timedelta(days=40)
        start_date = datetime.date.today()
        with self.assertRaises(ValueError):
            await self.client.fetch_cm_post_archive(start_date, end_date)

    async def test_client_fetch_cm_post_archive_invalid_page(self):
        """Testing fetching the CM Post Archive with invalid page number"""
        start_date = datetime.date.today()-datetime.timedelta(days=40)
        end_date = datetime.date.today()
        with self.assertRaises(ValueError):
            await self.client.fetch_cm_post_archive(start_date, end_date, -1)

    @aioresponses()
    async def test_client_fetch_current_auctions(self, mock):
        """Testing fetching the current auctions"""
        content = self.load_resource(FILE_BAZAAR_CURRENT)
        mock.get(CharacterBazaar.get_current_auctions_url(), status=200, body=content)
        response = await self.client.fetch_current_auctions()
        self.assertIsInstance(response.data, CharacterBazaar)

    async def test_client_fetch_current_auctions_invalid_page(self):
        """Testing fetching the current auctions with an invalid page"""
        with self.assertRaises(ValueError):
            await self.client.fetch_current_auctions(-1)

    @aioresponses()
    async def test_client_fetch_auction_history(self, mock):
        """Testing fetching the auction history"""
        content = self.load_resource(FILE_BAZAAR_HISTORY)
        mock.get(CharacterBazaar.get_auctions_history_url(), status=200, body=content)
        response = await self.client.fetch_auction_history()
        self.assertIsInstance(response.data, CharacterBazaar)

    async def test_client_fetch_auction_history_invalid_page(self):
        """Testing fetching the auction history with an incorrect page"""
        with self.assertRaises(ValueError):
            await self.client.fetch_auction_history(-1)

    @aioresponses()
    async def test_client_fetch_auction(self, mock):
        """Testing fetching an auction"""
        content = self.load_resource(FILE_AUCTION_FINISHED)
        mock.get(Auction.get_url(134), status=200, body=content)
        response = await self.client.fetch_auction(134)
        self.assertIsInstance(response.data, Auction)

    async def test_client_fetch_auction_invalid_id(self):
        """Testing fetching an auction with an invalid id"""
        with self.assertRaises(ValueError):
            await self.client.fetch_auction(-1)

    @aioresponses()
    async def test_client_fetch_event_calendar(self, mock):
        """Testing fetching the auction history"""
        content = self.load_resource(FILE_EVENT_CALENDAR)
        mock.get(EventSchedule.get_url(), status=200, body=content)
        response = await self.client.fetch_event_schedule()
        self.assertIsInstance(response.data, EventSchedule)

    async def test_client_fetch_event_calendar_invalid_params(self):
        """Testing fetching the auction history"""
        with self.assertRaises(ValueError):
            await self.client.fetch_event_schedule(3)

    @aioresponses()
    async def test_client_fetch_forum_community_boards(self, mock):
        """Testing fetching the community boards"""
        content = self.load_resource(FILE_WORLD_BOARDS)
        mock.get(BoardEntry.get_community_boards_url(), status=200, body=content)
        response = await self.client.fetch_forum_community_boards()
        self.assertIsInstance(response.data[0], BoardEntry)

    @aioresponses()
    async def test_client_fetch_forum_trade_boards(self, mock):
        """Testing fetching the trade boards"""
        content = self.load_resource(FILE_WORLD_BOARDS)
        mock.get(BoardEntry.get_trade_boards_url(), status=200, body=content)
        response = await self.client.fetch_forum_trade_boards()
        self.assertIsInstance(response.data[0], BoardEntry)

    @aioresponses()
    async def test_client_fetch_forum_support_boards(self, mock):
        """Testing fetching the support boards"""
        content = self.load_resource(FILE_WORLD_BOARDS)
        mock.get(BoardEntry.get_support_boards_url(), status=200, body=content)
        response = await self.client.fetch_forum_support_boards()
        self.assertIsInstance(response.data[0], BoardEntry)

    @aioresponses()
    async def test_client_fetch_forum_world_boards(self, mock):
        """Testing fetching the world boards"""
        content = self.load_resource(FILE_WORLD_BOARDS)
        mock.get(BoardEntry.get_world_boards_url(), status=200, body=content)
        response = await self.client.fetch_forum_world_boards()
        self.assertIsInstance(response.data[0], BoardEntry)

    @aioresponses()
    async def test_client_fetch_forum_board(self, mock):
        """Testing fetching a forum board"""
        content = self.load_resource(FILE_BOARD_THREAD_LIST)
        mock.get(BoardEntry.get_url(1), status=200, body=content)
        response = await self.client.fetch_forum_board(1)
        self.assertIsInstance(response.data, ForumBoard)

    @aioresponses()
    async def test_client_fetch_leaderboards(self, mock):
        """Testing fetching the leaderboards"""
        content = self.load_resource(FILE_LEADERBOARD_CURRENT)
        mock.get(Leaderboard.get_url("Antica"), status=200, body=content)
        response = await self.client.fetch_leaderboard("Antica")
        self.assertIsInstance(response.data, Leaderboard)

    @unittest.mock.patch("tibiapy.bazaar.Auction._parse_page_items")
    @unittest.skipIf(sys.version_info < (3, 8, 0), "AsyncMock was implemented in 3.8")
    async def test_client__fetch_all_pages_success(self, parse_page_items):
        """Testing internal method to fetch all pages of an auction item collection."""
        paginator = tibiapy.ItemSummary(page=1, total_pages=5)
        self.client._fetch_ajax_page = unittest.mock.AsyncMock()

        await self.client._fetch_all_pages(1, paginator, 1)

        self.assertEqual(4, self.client._fetch_ajax_page.await_count)
        self.assertEqual(4, parse_page_items.call_count)

    async def test_client__fetch_all_pages_none_input(self):
        """Testing internal method to fetch all pages of an auction item collection."""
        self.assertIsNone(await self.client._fetch_all_pages(1, None, 1))