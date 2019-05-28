import asyncio
import datetime

import aiohttp

import tibiapy
from tibiapy import Character, Guild, World, House, KillStatistics, ListedGuild, Highscores, Category, VocationFilter, \
    ListedHouse, HouseType, WorldOverview, NewsCategory, NewsType, ListedNews, News

__all__ = ("Client",)


class Client:
    """An asynchronous client that fetches information from Tibia.com

    .. versionadded:: 2.0.0

    Attributes
    ----------
    loop : :class:`asyncio.AbstractEventLoop`
        The event loop to use. The default one will be used if not defined.
    session: :class:`aiohttp.ClientSession`
        The client session that will be used for the requests. One will be created by default.
    """
    def __init__(self, loop=None, session=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop  # type: asyncio.AbstractEventLoop
        if session is not None:
            self.session = session  # type: aiohttp.ClientSession
        else:
            self.loop.create_task(self._initialize_session())

    async def _initialize_session(self):
        self.session = aiohttp.ClientSession()  # type: aiohttp.ClientSession

    async def _get(self, url):
        async with self.session.get(url) as resp:
            return await resp.text()

    async def _post(self, url, data):
        async with self.session.post(url, data=data) as resp:
            return await resp.text()

    async def fetch_character(self, name):
        """Fetches a character by its name from Tibia.com

        Parameters
        ----------
        name: :class:`str`
            The name of the character.

        Returns
        -------
        :class:`Character`
            The character if found, else ``None``.
        """
        content = await self._get(Character.get_url(name.strip()))
        char = Character.from_content(content)
        return char

    async def fetch_guild(self, name):
        """Fetches a guild by its name from Tibia.com

        Parameters
        ----------
        name: :class:`str`
            The name of the guild. The case must match exactly.

        Returns
        -------
        :class:`Guild`
            The guild if found, else ``None``.
        """
        content = await self._get(Guild.get_url(name))
        guild = Guild.from_content(content)
        return guild

    async def fetch_house(self, house_id, world):
        """Fetches a house in a specific world by its id.

        Parameters
        ----------
        house_id: :class:`int`
            The house's internal id.
        world: :class:`str`
            The name of the world to look for.

        Returns
        -------
        :class:`House`
            The house if found, ``None`` otherwise.
        """
        content = await self._get(House.get_url(house_id, world))
        house = House.from_content(content)
        return house

    async def fetch_highscores_page(self, world, category=Category.EXPERIENCE,
                                    vocation=VocationFilter.ALL, page=1):
        """Fetches a single highscores page from Tibia.com

        Parameters
        ----------
        world: :class:`str`
            The world to search the highscores in.
        category: :class:`Category`
            The highscores category to search, by default Experience.
        vocation: :class:`VocationFilter`
            The vocation filter to use. No filter used by default.
        page: :class:`int`
            The page to fetch, by default the first page is fetched.

        Returns
        -------
        :class:`Highscores`
            The highscores information or ``None`` if not found.
        """
        content = await self._get(Highscores.get_url(world, category, vocation, page))
        highscores = Highscores.from_content(content)
        return highscores

    async def fetch_kill_statistics(self, world):
        """Fetches the kill statistics of a world from Tibia.com.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`KillStatistics`
            The kill statistics of the world if found.
        """
        content = await self._get(KillStatistics.get_url(world))
        kill_statistics = KillStatistics.from_content(content)
        return kill_statistics

    async def fetch_world(self, name):
        """Fetches a world from Tibia.com

        Parameters
        ----------
        name: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`World`
            The world's information if found, ```None`` otherwise.
        """
        content = await self._get(World.get_url(name))
        world = World.from_content(content)
        return world

    async def fetch_world_houses(self, world, town, house_type=HouseType.HOUSE):
        """Fetches the house list of a world and type.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        town: :class:`str`
            The name of the town.
        house_type: :class:`HouseType`
            The type of building. House by default.

        Returns
        -------
        list of :class:`ListedHouse`
            The lists of houses meeting the criteria if found.
        """
        content = await self._get(ListedHouse.get_list_url(world, town, house_type))
        houses = ListedHouse.list_from_content(content)
        return houses

    async def fetch_world_guilds(self, world: str):
        """Fetches the list of guilds in a world from Tibia.com

        Parameters
        ----------
        world: :class:`str`
            The name of the world.

        Returns
        -------
        list of :class:`ListedGuild`
            The lists of guilds in the world.
        """
        content = await self._get(ListedGuild.get_world_list_url(world))
        guilds = ListedGuild.list_from_content(content)
        return guilds

    async def fetch_world_list(self):
        """Fetches the world overview information from Tibia.com.

        Returns
        -------
        :class:`WorldOverview`
            The world overview information.
        """
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
        list of :class:`ListedNews`
            The news meeting the search criteria.
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
        """Fetches all the published news in the last specified days.

        Parameters
        ----------
        days: :class:`int`
            The number of days to search, by default 30.

        Returns
        -------
        list of :class:`ListedNews`
            The news posted in the last specified days.
        """
        end = datetime.date.today()
        begin = end - datetime.timedelta(days=days)
        return await self.fetch_news_archive(begin, end)

    async def fetch_news(self, news_id):
        """Fetches a news entry by its id from Tibia.com

        Parameters
        ----------
        news_id: :class:`int`
            The id of the news entry.

        Returns
        -------
        :class:`News`
            The news entry if found, ``None`` otherwise.
        """
        content = await self._get(News.get_url(news_id))
        news = News.from_content(content, news_id)
        return news
