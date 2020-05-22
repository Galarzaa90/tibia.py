import asyncio
import datetime

import aiohttp
import aiohttp_socks

import tibiapy
from tibiapy import BoostedCreature, Category, Character, Forbidden, Guild, Highscores, House, HouseOrder, HouseStatus, \
    HouseType, KillStatistics, ListedGuild, ListedHouse, ListedNews, NetworkError, News, NewsCategory, NewsType, \
    Tournament, TournamentLeaderboard, VocationFilter, World, WorldOverview

__all__ = (
    "Client",
)

# Tibia.com's cache for the community section is 5 minutes.
# This limit is not sent anywhere, so there's no way to automate it.
CACHE_LIMIT = 300


# This class is not used in this release.
class _TibiaResponse:  # pragma: no cover
    def __init__(self, data=None, cache_limit=CACHE_LIMIT, **kwargs):
        self.data = None
        self.cached = kwargs.get("cached")
        self.cache_age = kwargs.get("cache_age")
        self.response_timestamp = None
        self.data_timestamp = None
        self.parsing_time = None
        self.response_time = None


class Client:
    """An asynchronous client that fetches information from Tibia.com

    The client uses a :class:`aiohttp.ClientSession` to request the information.
    A single session is shared across all operations.

    If desired, a custom ClientSession instance may be passed, instead of creating a new one.

    .. versionadded:: 2.0.0

    Attributes
    ----------
    loop : :class:`asyncio.AbstractEventLoop`
        The event loop to use. The default one will be used if not defined.
    session: :class:`aiohttp.ClientSession`
        The client session that will be used for the requests. One will be created by default.
    proxy_url: :class:`str`
        The URL of the SOCKS proxy to use for requests.
        Note that if a session is passed, the SOCKS proxy won't be used and must be applied when creating the session.
    """

    def __init__(self, loop=None, session=None, *, proxy_url=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop  # type: asyncio.AbstractEventLoop
        if session is not None:
            self.session = session  # type: aiohttp.ClientSession
        else:
            self.loop.create_task(self._initialize_session(proxy_url))

    async def _initialize_session(self, proxy_url=None):
        headers = {
            'User-Agent': "Tibia.py/%s (+https://github.com/Galarzaa90/tibia.py)" % tibiapy.__version__,
            'Accept-Encoding': "deflate, gzip"
        }
        connector = aiohttp_socks.SocksConnector.from_url(proxy_url) if proxy_url else None
        self.session = aiohttp.ClientSession(loop=self.loop, headers=headers,
                                             connector=connector)  # type: aiohttp.ClientSession

    @classmethod
    def _handle_status(cls, status_code):
        """Handles error status codes, raising exceptions if necessary."""
        if status_code < 400:
            return
        if status_code == 403:
            raise Forbidden("403 Forbidden: Might be getting rate-limited")
        else:
            raise NetworkError("Request error, status code: %d" % status_code)

    async def _get(self, url):
        """Base GET request, handling possible error statuses.
        
        Parameters
        ----------
        url: :class:`str`
            The URL that will be requested.

        Returns
        -------
        :class:`str`
            The text content of the response.

        Raises
        ------
        Forbidden:
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        try:
            async with self.session.get(url, compress=True) as resp:
                self._handle_status(resp.status)
                return await resp.text()
        except aiohttp.ClientError as e:
            raise NetworkError("aiohttp.ClientError: %s" % e, e)
        except aiohttp_socks.SocksConnectionError as e:
            raise NetworkError("aiohttp_socks.SocksConnectionError: %s" % e, e)
        except UnicodeDecodeError as e:
            raise NetworkError('UnicodeDecodeError: %s' % e, e)

    async def _post(self, url, data):
        """Base POST request, handling possible error statuses.

        Parameters
        ----------
        url: :class:`str`
            The URL that will be requested.
        data: :class:`dict`
            A mapping representing the form-data to send as part of the request.

        Returns
        -------
        :class:`str`
            The text content of the response.
        """
        try:
            async with self.session.post(url, data=data) as resp:
                self._handle_status(resp.status)
                return await resp.text()
        except aiohttp.ClientError as e:
            raise NetworkError("aiohttp.ClientError: %s" % e, e)
        except aiohttp_socks.SocksConnectionError as e:
            raise NetworkError("aiohttp_socks.SocksConnectionError: %s" % e, e)
        except UnicodeDecodeError as e:
            raise NetworkError('UnicodeDecodeError: %s' % e, e)

    async def fetch_boosted_creature(self):
        """Fetches today's boosted creature.

        .. versionadded:: 2.1.0

        Returns
        -------
        :class:`BoostedCreature`
            The boosted creature of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(News.get_list_url())
        boosted_creature = BoostedCreature.from_content(content)
        return boosted_creature

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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(World.get_url(name))
        world = World.from_content(content)
        return world

    async def fetch_world_houses(self, world, town, house_type=HouseType.HOUSE, status: HouseStatus = None,
                                 order=HouseOrder.NAME):
        """Fetches the house list of a world and type.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        town: :class:`str`
            The name of the town.
        house_type: :class:`HouseType`
            The type of building. House by default.
        status: :class:`HouseStatus`, optional
            The house status to filter results. By default no filters will be applied.
        order: :class:`HouseOrder`, optional
            The ordering to use for the results. By default they are sorted by name.

        Returns
        -------
        list of :class:`ListedHouse`
            The lists of houses meeting the criteria if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(ListedHouse.get_list_url(world, town, house_type, status, order))
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
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

        Raises
        ------
        ValueError:
            If ``begin_date`` is more recent than ``end_date``.
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        if begin_date > end_date:
            raise ValueError("begin_date can't be more recent than end_date")
        if not categories:
            categories = list(NewsCategory)
        if not types:
            types = list(NewsType)
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

        content = await self._post(News.get_list_url(), data)
        news = ListedNews.list_from_content(content)
        return news

    async def fetch_recent_news(self, days=30, categories=None, types=None):
        """Fetches all the published news in the last specified days.

        This is a shortcut for :meth:`fetch_news_archive`, to handle dates more easily.

        Parameters
        ----------
        days: :class:`int`
            The number of days to search, by default 30.
        categories: `list` of :class:`NewsCategory`
            The allowed categories to show. If left blank, all categories will be searched.
        types : `list` of :class:`ListedNews`
            The allowed news types to show. if unused, all types will be searched.

        Returns
        -------
        list of :class:`ListedNews`
            The news posted in the last specified days.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        end = datetime.date.today()
        begin = end - datetime.timedelta(days=days)
        return await self.fetch_news_archive(begin, end, categories, types)

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

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(News.get_url(news_id))
        news = News.from_content(content, news_id)
        return news

    async def fetch_tournament(self, tournament_cycle=0):
        """Fetches a tournament from Tibia.com

        Parameters
        ----------
        tournament_cycle: :class:`int`
            The cycle of the tournament. if unspecified, it will get the currently running tournament.

        Returns
        -------
        :class:`Tournament`
            The tournament if found, ``None`` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(Tournament.get_url(tournament_cycle))
        tournament = Tournament.from_content(content)
        return tournament

    async def fetch_tournament_leaderboard(self, tournament_cycle, world, page=1):
        """Fetches a tournament leaderboard from Tibia.com

        Parameters
        ----------
        tournament_cycle: :class:`int`
            The cycle of the tournament. if unspecified, it will get the currently running tournament.
        world: :class:`str`
            The name of the world to get the leaderboards for.
        page: :class:`int`
            The desired leaderboards page, by default 1 is used.

        Returns
        -------
        :class:`TournamentLeaderboard`
            The tournament's leaderboard if found, ``None`` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        content = await self._get(TournamentLeaderboard.get_url(world, tournament_cycle, page))
        tournament_leaderboard = TournamentLeaderboard.from_content(content)
        return tournament_leaderboard

