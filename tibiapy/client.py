import asyncio
import datetime

import aiohttp

import tibiapy
from tibiapy import Character, Guild, World, House, KillStatistics, ListedGuild, Highscores, Category, VocationFilter, \
    ListedHouse, HouseType, WorldOverview, NewsCategory, NewsType, ListedNews, News

__all__ = ("Client",)


class Client():
    def __init__(self, loop=None, session=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop  # type: asyncio.AbstractEventLoop
        if session is not None:
            self.session = session
        self.loop.create_task(self._initialize_session())

    async def _initialize_session(self):
        self.session = aiohttp.ClientSession()

    async def _get(self, url):
        async with self.session.get(url) as resp:
            return await resp.text()

    async def _post(self, url, data):
        async with self.session.post(url, data=data) as resp:
            return await resp.text()

    async def fetch_character(self, name):
        content = await self._get(Character.get_url(name))
        char = Character.from_content(content)
        return char

    async def fetch_guild(self, name):
        content = await self._get(Guild.get_url(name))
        guild = Guild.from_content(content)
        return guild

    async def fetch_house(self, house_id: int, world: str):
        content = await self._get(House.get_url(house_id, world))
        house = House.from_content(content)
        return house

    async def fetch_highscores_page(self, world, category=Category.EXPERIENCE,
                                    vocation=VocationFilter.ALL, page=1):
        content = await self._get(Highscores.get_url(world, category, vocation, page))
        highscores = Highscores.from_content(content)
        return highscores

    async def fetch_kill_statistics(self, world: str):
        content = await self._get(KillStatistics.get_url(world))
        kill_statistics = KillStatistics.from_content(content)
        return kill_statistics

    async def fetch_world(self, name: str):
        content = await self._get(World.get_url(name))
        world = World.from_content(content)
        return world

    async def fetch_world_houses(self, world, town, house_type=HouseType.HOUSE):
        content = await self._get(ListedHouse.get_list_url(world, town, house_type))
        houses = ListedHouse.list_from_content(content)
        return houses

    async def fetch_world_guilds(self, world: str):
        content = await self._get(ListedGuild.get_world_list_url(world))
        guilds = ListedGuild.list_from_content(content)
        return guilds

    async def fetch_world_list(self):
        content = await self._get(WorldOverview.get_url())
        world_overview = WorldOverview.from_content(content)
        return world_overview

    async def fetch_news_archive(self, begin_date, end_date, categories=None, types=None):
        """Fetches news from the archive meeting the search criteria.

        Parameters
        ----------
        begin_date: :class:`datetime.date`
            The beginning date to search dates in.
        end_date: :class:`datetime.date`
            The end date to search dates in.
        categories: `list` of :class:`NewsCategory`
            The allowed categories to show. If left blank, all categories will be searched.
        types : `list` of :class:`ListedNews`
            The allowed news types to show. if unused, all types will be searched.
        Returns
        -------

        """
        if begin_date > end_date:
            raise ValueError("begin_date can't be more recent than end_date")
        if not categories:
            categories = NewsCategory.items()
        if not types:
            types = NewsType.items()
        data = {
            "filter_begin_day": begin_date.day,
            "filter_begin_month": begin_date.month,
            "filter_begin_year": begin_date.year,
            "filter_end_day": end_date.day,
            "filter_end_month": end_date.month,
            "filter_end_year": end_date.year,
        }
        for category in categories:
            key = "filter_%s" % category.value
            data[key] = category.value
        if NewsType.FEATURED_ARTICLE in types:
            data["filter_article"] = "article"
        if NewsType.NEWS in types:
            data["filter_news"] = "news"
        if NewsType.NEWS_TICKER in types:
            data["filter_ticker"] = "ticker"

        content = await self._post(tibiapy.news.NEWS_SEARCH_URL, data)
        news = ListedNews.list_from_content(content)
        return news

    async def fetch_recent_news(self, days=30):
        end = datetime.date.today()
        begin = end - datetime.timedelta(days=days)
        return await self.fetch_news_archive(begin, end)

    async def fetch_news(self, news_id):
        content = await self._get(News.get_url(news_id))
        news = News.from_content(content, news_id)
        return news
