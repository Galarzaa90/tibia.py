import datetime

import aiohttp
import asynctest
from aioresponses import aioresponses

from tests.tests_character import FILE_CHARACTER_RESOURCE, FILE_CHARACTER_NOT_FOUND
from tests.tests_guild import FILE_GUILD_FULL, FILE_GUILD_LIST
from tests.tests_highscores import FILE_HIGHSCORES_FULL
from tests.tests_house import FILE_HOUSE_FULL, FILE_HOUSE_LIST
from tests.tests_kill_statistics import FILE_KILL_STATISTICS_FULL
from tests.tests_news import FILE_NEWS_LIST, FILE_NEWS_ARTICLE
from tests.tests_tibiapy import TestCommons
from tests.tests_world import FILE_WORLD_FULL, FILE_WORLD_LIST
from tibiapy import Client, Character, Guild, Highscores, VocationFilter, Category, House, ListedHouse, ListedGuild, \
    KillStatistics, ListedNews, News, World, WorldOverview, Forbidden, NetworkError, BoostedCreature


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

        mock.get(ListedNews.get_list_url(), exception=aiohttp.ClientError())
        with self.assertRaises(NetworkError):
            await self.client.fetch_world_list()

        mock.post(ListedNews.get_list_url(), exception=aiohttp.ClientOSError())
        with self.assertRaises(NetworkError):
            await self.client.fetch_recent_news(30)

    @aioresponses()
    async def test_client_fetch_character(self, mock):
        """Testing fetching a character"""
        name = "Tschas"
        content = self._load_resource(FILE_CHARACTER_RESOURCE)
        mock.get(Character.get_url(name), status=200, body=content)
        character = await self.client.fetch_character(name)

        self.assertIsInstance(character, Character)

    @aioresponses()
    async def test_client_fetch_character_not_found(self, mock):
        """Testing fetching a non existent character"""
        name = "Nezune"
        content = self._load_resource(FILE_CHARACTER_NOT_FOUND)
        mock.get(Character.get_url(name), status=200, body=content)
        character = await self.client.fetch_character(name)

        self.assertIsNone(character)

    @aioresponses()
    async def test_client_fetch_guild(self, mock):
        """Testing fetching a guild"""
        name = "Vitam et Mortem"
        content = self._load_resource(FILE_GUILD_FULL)
        mock.get(Guild.get_url(name), status=200, body=content)
        guild = await self.client.fetch_guild(name)

        self.assertIsInstance(guild, Guild)

    @aioresponses()
    async def test_client_fetch_world_guilds(self, mock):
        """Testing fetching a world's guild list"""
        world = "Zuna"
        content = self._load_resource(FILE_GUILD_LIST)
        mock.get(ListedGuild.get_world_list_url(world), status=200, body=content)
        guilds = await self.client.fetch_world_guilds(world)

        self.assertIsInstance(guilds[0], ListedGuild)

    @aioresponses()
    async def test_client_fetch_highscores_page(self, mock):
        """Testing fetching a highscores page"""
        world = "Estela"
        category = Category.MAGIC_LEVEL
        vocations = VocationFilter.KNIGHTS
        content = self._load_resource(FILE_HIGHSCORES_FULL)
        mock.get(Highscores.get_url(world, category, vocations), status=200, body=content)
        highscores = await self.client.fetch_highscores_page(world, category, vocations)

        self.assertIsInstance(highscores, Highscores)

    @aioresponses()
    async def test_client_fetch_house(self, mock):
        """Testing fetching a house"""
        world = "Antica"
        house_id = 5236
        content = self._load_resource(FILE_HOUSE_FULL)
        mock.get(House.get_url(house_id, world), status=200, body=content)
        house = await self.client.fetch_house(house_id, world)

        self.assertIsInstance(house, House)

    @aioresponses()
    async def test_client_fetch_world_houses(self, mock):
        """Testing fetching a world's houses"""
        world = "Antica"
        city = "Edron"
        content = self._load_resource(FILE_HOUSE_LIST)
        mock.get(ListedHouse.get_list_url(world, city), status=200, body=content)
        houses = await self.client.fetch_world_houses(world, city)

        self.assertIsInstance(houses, list)
        self.assertIsInstance(houses[0], ListedHouse)

    @aioresponses()
    async def test_client_fetch_kill_statistics(self, mock):
        """Testing fetching kill statistics"""
        world = "Antica"
        content = self._load_resource(FILE_KILL_STATISTICS_FULL)
        mock.get(KillStatistics.get_url(world), status=200, body=content)
        kill_statistics = await self.client.fetch_kill_statistics(world)

        self.assertIsInstance(kill_statistics, KillStatistics)

    @aioresponses()
    async def test_client_fetch_recent_news(self, mock):
        """Testing fetching recent nows"""
        content = self._load_resource(FILE_NEWS_LIST)
        mock.post(ListedNews.get_list_url(), status=200, body=content)
        recent_news = await self.client.fetch_recent_news(30)

        self.assertIsInstance(recent_news, list)
        self.assertIsInstance(recent_news[0], ListedNews)

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
        content = self._load_resource(FILE_NEWS_ARTICLE)
        mock.get(News.get_url(news_id), status=200, body=content)
        news = await self.client.fetch_news(news_id)

        self.assertIsInstance(news, News)

    @aioresponses()
    async def test_client_fetch_world(self, mock):
        """Testing fetching a world"""
        name = "Antica"
        content = self._load_resource(FILE_WORLD_FULL)
        mock.get(World.get_url(name), status=200, body=content)
        world = await self.client.fetch_world(name)

        self.assertIsInstance(world, World)

    @aioresponses()
    async def test_client_fetch_world_list(self, mock):
        """Testing fetching the world list"""
        content = self._load_resource(FILE_WORLD_LIST)
        mock.get(WorldOverview.get_url(), status=200, body=content)
        worlds = await self.client.fetch_world_list()

        self.assertIsInstance(worlds, WorldOverview)

    @aioresponses()
    async def test_client_fetch_boosted_creature(self, mock):
        """Testing fetching the boosted creature"""
        content = self._load_resource(self.FILE_UNRELATED_SECTION)
        mock.get(News.get_list_url(), status=200, body=content)
        creature = await self.client.fetch_boosted_creature()

        self.assertIsInstance(creature, BoostedCreature)



