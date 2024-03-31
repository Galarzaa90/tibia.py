"""Asynchronous Tibia.com client."""
from __future__ import annotations

import asyncio
import datetime
import json
import logging
import time
from typing import Any, Callable, Dict, Optional, Set, TYPE_CHECKING, TypeVar

import aiohttp
import aiohttp_socks

import tibiapy
from tibiapy.enums import (BazaarType, HighscoresBattlEyeType, HighscoresCategory, HighscoresProfession, HouseOrder,
                           HouseStatus, HouseType, NewsCategory, NewsType, PvpTypeFilter, SpellGroup, SpellSorting,
                           SpellType, SpellVocationFilter)
from tibiapy.errors import ForbiddenError, NetworkError, SiteMaintenanceError
from tibiapy.models import TibiaResponse
from tibiapy.parsers import (
    AuctionParser, BoostableBossesParser, BoostedCreaturesParser, CMPostArchiveParser, CharacterBazaarParser,
    CharacterParser, CreatureParser, CreaturesSectionParser, EventScheduleParser, FansitesSectionParser,
    ForumAnnouncementParser,
    ForumBoardParser, ForumSectionParser, ForumThreadParser, GuildParser, GuildWarsParser, GuildsSectionParser,
    HighscoresParser, HouseParser, HousesSectionParser, KillStatisticsParser, LeaderboardParser, NewsArchiveParser,
    NewsParser, SpellParser, SpellsSectionParser, WorldOverviewParser, WorldParser,
)
from tibiapy.urls import (
    get_auction_url, get_bazaar_url, get_boostable_bosses_url, get_character_url, get_cm_post_archive_url,
    get_community_boards_url, get_creature_url, get_creatures_section_url, get_event_schedule_url,
    get_fansites_url, get_forum_announcement_url, get_forum_board_url, get_forum_post_url, get_forum_section_url,
    get_forum_thread_url,
    get_guild_url, get_guild_wars_url, get_highscores_url, get_house_url, get_houses_section_url,
    get_kill_statistics_url, get_leaderboards_url, get_news_archive_url, get_news_url, get_spell_url,
    get_spells_section_url, get_support_boards_url, get_trade_boards_url, get_world_boards_url, get_world_guilds_url,
    get_world_overview_url, get_world_url,
)

if TYPE_CHECKING:
    from tibiapy.models import (
        AjaxPaginator, Auction, AuctionFilters, BoostableBosses, BoostedCreatures, BossEntry, CMPostArchive, Character,
        CharacterBazaar, Creature, CreatureEntry, CreaturesSection, EventSchedule, FansitesSection, ForumAnnouncement,
        ForumBoard, ForumSection, ForumThread, Guild, GuildWars, GuildsSection, Highscores, House, HousesSection,
        KillStatistics, Leaderboard, News, NewsArchive, Spell, SpellsSection, World, WorldOverview,
    )

__all__ = (
    "Client",
)

T = TypeVar("T")

log = logging.getLogger("tibiapy")


class _RawResponse:
    def __init__(self, response: aiohttp.ClientResponse, fetching_time: float):
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.fetching_time = fetching_time
        self.url = response.url
        self.cached = response.headers.get("CF-Cache-Status") == "HIT"
        age = response.headers.get("Age")
        self.age = int(age) if age is not None and age.isnumeric() else 0
        self.content = None

    def __repr__(self):
        return (f"<{self.__class__.__name__} timestamp={self.timestamp!r} fetching_time={self.fetching_time!r} "
                f"cached={self.cached!r} age={self.age!r}>")

    def parse(self, parser: Callable[[str], T]) -> TibiaResponse[T]:
        start_time = time.perf_counter()
        data = parser(self.content)
        parsing_time = time.perf_counter() - start_time
        log.info("%s | PARSE | %dms", self.url, int(parsing_time * 1000))
        return TibiaResponse.from_raw(self, data, parsing_time)


class Client:
    """An asynchronous client that fetches information from Tibia.com.

    The client uses a :class:`aiohttp.ClientSession` to request the information.
    A single session is shared across all operations.

    If desired, a custom ClientSession instance may be passed, instead of creating a new one.

    .. versionadded:: 2.0.0

    .. versionchanged:: 3.0.0
        All methods return a :class:`TibiaResponse` instance, containing additional information such as cache age.

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

    def __init__(
            self,
            loop: asyncio.AbstractEventLoop = None,
            session: aiohttp.ClientSession = None,
            *,
            proxy_url: str = None,
    ):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        self._session_ready = asyncio.Event()
        self.proxy_url = proxy_url
        if session is not None:
            self.session: aiohttp.ClientSession = session
            self._session_ready.set()
        else:
            self.loop.create_task(self._initialize_session(proxy_url))

    # region Private Methods

    async def _initialize_session(self, proxy_url: str = None):
        """Initialize the aiohttp session object."""
        headers = {
            "User-Agent": f"Tibia.py/{tibiapy.__version__} (+https://github.com/Galarzaa90/tibia.py)",
            "Accept-Encoding": "deflate, gzip",
        }
        connector = aiohttp_socks.SocksConnector.from_url(proxy_url) if proxy_url else None
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(
            loop=self.loop,
            headers=headers,
            connector=connector,
        )
        self._session_ready.set()

    @classmethod
    def _handle_status(cls, status_code: int, fetching_time: float = 0.0) -> None:
        """Handle error status codes, raising exceptions if necessary."""
        if status_code < 400:
            return

        if status_code == 403:
            raise ForbiddenError("403 Forbidden: Might be getting rate-limited", fetching_time=fetching_time)

        raise NetworkError(f"Request error, status code: {status_code:d}", fetching_time=fetching_time)

    async def _request(
            self,
            method: str,
            url: str,
            data: Dict[str, Any] = None,
            headers: Dict[str, Any] = None,
            *,
            test: bool = False,
    ):
        """Perform the HTTP request, handling possible error statuses.

        Parameters
        ----------
        method: :class:`str`
            The HTTP method to use for the request.
        url: :class:`str`
            The URL that will be requested.
        data: :class:`dict`
            A mapping representing the form-data to send as part of the request.
        headers: :class:`dict`
            A mapping representing the headers to send as part of the request.
        test:
            Whether to request the test website instead.

        Returns
        -------
        :class:`_RawResponse`
            The raw response obtained from the server.

        Raises
        ------
        Forbidden:
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        await self._session_ready.wait()
        if test:
            url = url.replace("www.tibia.com", "www.test.tibia.com")

        init_time = time.perf_counter()
        try:
            async with self.session.request(method, url, data=data, headers=headers) as resp:
                diff_time = time.perf_counter() - init_time
                if "maintenance.tibia.com" in str(resp.url):
                    log.info("%s | %s | %s %s | maintenance.tibia.com", url, resp.method, resp.status, resp.reason)
                    raise SiteMaintenanceError("Tibia.com is down for maintenance.")

                log.info("%s | %s | %s %s | %dms", url, resp.method, resp.status, resp.reason, int(diff_time * 1000))
                self._handle_status(resp.status, diff_time)
                response = _RawResponse(resp, diff_time)
                response.content = await resp.text()
                return response
        except aiohttp.ClientError as e:
            raise NetworkError(f"aiohttp.ClientError: {e}", e, time.perf_counter() - init_time) from e
        except aiohttp_socks.SocksConnectionError as e:
            raise NetworkError(f"aiohttp_socks.SocksConnectionError: {e}", e, time.perf_counter() - init_time) from e
        except UnicodeDecodeError as e:
            raise NetworkError(f"UnicodeDecodeError: {e}", e, time.perf_counter() - init_time) from e

    async def _fetch_all_pages(self, auction_id: int, paginator: AjaxPaginator, item_type: int, *, test: bool = False):
        """Fetch all the pages of an auction paginator.

        Parameters
        ----------
        auction_id: :class:`int`
            The id of the auction.
        paginator:
            The paginator object
        item_type: :class:`int`
            The item type.
        test:
            Whether to request the test website instead.
        """
        current_page = 2
        while current_page <= paginator.total_pages:
            content = await self._fetch_ajax_page(auction_id, item_type, current_page, test=test)
            if content:
                # noinspection PyProtectedMember
                entries = AuctionParser._parse_page_items(content, paginator)
                paginator.entries.extend(entries)

            current_page += 1

        paginator.is_fully_fetched = True

    async def _fetch_ajax_page(self, auction_id: int, type_id: int, page: int, *, test: bool = False):
        """Fetch an ajax page from the paginated summaries in the auction section.

        Parameters
        ----------
        auction_id: :class:`int`
            The id of the auction.
        type_id: :class:`int`
            The ID of the type of the catalog to check.
        page: :class:`int`
            The page number to fetch.
        test:
            Whether to request the test website instead.

        Returns
        -------
        :class:`str`:
            The HTML content of the obtained page.
        """
        headers = {"x-requested-with": "XMLHttpRequest"}
        page_response = await self._request(
            "GET",
            f"https://www.tibia.com/websiteservices/handle_charactertrades.php?"
            f"auctionid={auction_id}&type={type_id}&currentpage={page}",
            headers=headers,
            test=test,
        )
        try:
            data = json.loads(page_response.content.replace("\x0a", " "))
        except json.decoder.JSONDecodeError:
            return None

        try:
            return data["AjaxObjects"][0]["Data"]
        except KeyError:
            return None

    # endregion

    # region Front Page

    async def fetch_boosted_creature(self, *, test: bool = False) -> TibiaResponse[CreatureEntry]:
        """Fetch today's boosted creature.

        .. versionadded:: 2.1.0
        .. versionchanged:: 4.0.0
            The return type of the data returned was changed to :class:`CreatureEntry`, previous type was removed.

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[CreatureEntry]
            The boosted creature of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_news_archive_url(), test=test)
        return response.parse(CreaturesSectionParser.boosted_creature_from_header)

    async def fetch_boosted_creature_and_boss(self, *, test: bool = False) -> TibiaResponse[BoostedCreatures]:
        """Fetch today's boosted creature and boss.

        .. versionadded:: 5.3.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[BoostedCreatures]
            The boosted creature and boss of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_news_archive_url(), test=test)
        return response.parse(BoostedCreaturesParser.from_header)

    # region Bosses
    async def fetch_boosted_boss(self, *, test: bool = False) -> TibiaResponse[BossEntry]:
        """Fetch today's boosted boss.

        .. versionadded:: 5.3.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[BossEntry]
            The boosted boss of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_news_archive_url(), test=test)
        return response.parse(BoostableBossesParser.boosted_boss_from_header)

    # endregion

    # region News
    async def fetch_news_archive(
            self,
            from_date: datetime.date,
            to_date: datetime.date = None,
            categories: Set[NewsCategory] = None,
            types: Set[NewsType] = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[NewsArchive]:
        """Fetch news from the archive meeting the search criteria.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`NewsArchive` instead.

        Parameters
        ----------
        from_date:
            The beginning date to search dates in.
        to_date:
            The end date to search dates in.
        categories:
            The allowed categories to show. If left blank, all categories will be searched.
        types:
            The allowed news types to show. if unused, all types will be searched.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[NewsArchive]
            The news meeting the search criteria.

        Raises
        ------
        :exc:`ValueError`:
            If ``begin_date`` is more recent than ``to_date``.
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        to_date = to_date or datetime.date.today()
        if from_date > to_date:
            raise ValueError("start_date can't be more recent than end_date")

        form_data = NewsArchiveParser.get_form_data(from_date, to_date, categories, types)
        response = await self._request("POST", get_news_archive_url(), form_data, test=test)
        return response.parse(NewsArchiveParser.from_content)

    async def fetch_news_archive_by_days(
            self,
            days: int = 30,
            categories: Set[NewsCategory] = None,
            types: Set[NewsType] = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[NewsArchive]:
        """Fetch all the published news in the last specified days.

        This is a shortcut for :meth:`fetch_news_archive`, to handle dates more easily.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`NewsArchive` instead.

        Parameters
        ----------
        days:
            The number of days to search, by default 30.
        categories:
            The allowed categories to show. If left blank, all categories will be searched.
        types:
            The allowed news types to show. if unused, all types will be searched.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[NewsArchive]
            The news posted in the last specified days.

        Raises
        ------
        :exc:`ValueError`:
            If ``days`` is lesser than zero.
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        if days < 0:
            raise ValueError("days must be zero or higher")

        end = datetime.date.today()
        begin = end - datetime.timedelta(days=days)
        return await self.fetch_news_archive(begin, end, categories, types, test=test)

    async def fetch_news(self, news_id: int, *, test: bool = False) -> TibiaResponse[Optional[News]]:
        """Fetch a news entry by its id from Tibia.com.

        Parameters
        ----------
        news_id:
            The ID of the news entry.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[News]
            The news entry if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_news_url(news_id), test=test)
        return response.parse(lambda r: NewsParser.from_content(r, news_id))

    async def fetch_event_schedule(
            self,
            month: int = None,
            year: int = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[EventSchedule]:
        """Fetch the event calendar. By default, it gets the events for the current month.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        month:
            The month of the events to display.
        year:
            The year of the events to display.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[EventSchedule]
            The event calendar.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If only one of year or month are defined.
        """
        if (year is None and month is not None) or (year is not None and month is None):
            raise ValueError("both year and month must be defined or neither must be defined.")

        response = await self._request("GET", get_event_schedule_url(month, year), test=test)
        return response.parse(EventScheduleParser.from_content)

    # endregion

    # region Library

    async def fetch_creatures(self, *, test: bool = False) -> TibiaResponse[CreaturesSection]:
        """Fetch the creatures from the library section.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[CreaturesSection]
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_creatures_section_url(), test=test)
        return response.parse(CreaturesSectionParser.from_content)

    async def fetch_creature(self, identifier: str, *, test: bool = False) -> TibiaResponse[Optional[Creature]]:
        """Fetch a creature's information from the Tibia.com library.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        identifier:
            The internal name of the race.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Creature]
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_creature_url(identifier), test=test)
        return response.parse(CreatureParser.from_content)

    async def fetch_boostable_bosses(self, *, test: bool = False) -> TibiaResponse[BoostableBosses]:
        """Fetch the boostable bosses from the library section.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`,BoostableBosses`
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_boostable_bosses_url(), test=test)
        return response.parse(BoostableBossesParser.from_content)

    async def fetch_spells(self, *,
                           vocation: Optional[SpellVocationFilter] = None,
                           group: Optional[SpellGroup] = None,
                           spell_type: Optional[SpellType] = None,
                           is_premium: Optional[bool] = None,
                           sort: Optional[SpellSorting] = None,
                           test: bool = False) -> TibiaResponse[SpellsSection]:
        """Fetch the spells section.

        Parameters
        ----------
        vocation:
            The vocation to filter in spells for.
        group:
            The spell's primary cooldown group.
        spell_type:
            The type of spells to show.
        is_premium:
            The type of premium requirement to filter. :obj:`None` means any premium requirement.
        sort:
            The field to sort spells by.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[SpellsSection]
            The spells section with the results.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_spells_section_url(vocation=vocation, group=group,
                                                                     spell_type=spell_type, is_premium=is_premium,
                                                                     sort=sort), test=test)
        return response.parse(SpellsSectionParser.from_content)

    async def fetch_spell(self, identifier: str, *, test: bool = False) -> TibiaResponse[Optional[Spell]]:
        """Fetch a spell by its identifier.

        Parameters
        ----------
        identifier:
            The spell's identifier. This is usually the name of the spell in lowercase and with no spaces.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Spell]]
            The spell if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_spell_url(identifier), test=test)
        return response.parse(SpellParser.from_content)

    # endregion

    # region Community

    async def fetch_character(self, name: str, *, test: bool = False) -> TibiaResponse[Optional[Character]]:
        """Fetch a character by its name from Tibia.com.

        Parameters
        ----------
        name:
            The name of the character.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Character]]
            A response containing the character, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_character_url(name.strip()), test=test)
        return response.parse(CharacterParser.from_content)

    async def fetch_world_overview(self, *, test: bool = False) -> TibiaResponse[WorldOverview]:
        """Fetch the world overview information from Tibia.com.

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[WorldOverview]
            A response containing the world overview information.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_world_overview_url(), test=test)
        return response.parse(WorldOverviewParser.from_content)

    async def fetch_world(self, name: str, *, test: bool = False) -> TibiaResponse[Optional[World]]:
        """Fetch a world from Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[World]]
            A response containing the world's information if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_world_url(name), test=test)
        return response.parse(WorldParser.from_content)

    async def fetch_highscores_page(
            self,
            world: str = None,
            category: HighscoresCategory = HighscoresCategory.EXPERIENCE,
            vocation: HighscoresProfession = HighscoresProfession.ALL,
            page: int = 1,
            battleye_type: Optional[HighscoresBattlEyeType] = None,
            pvp_types: Set[PvpTypeFilter] = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[Optional[Highscores]]:
        """Fetch a single highscores page from Tibia.com.

        Notes
        -----
        It is not possible to use BattlEye or PvPType filters when requesting a specific world.

        Parameters
        ----------
        world:
            The world to search the highscores in.
        category:
            The highscores category to search, by default Experience.
        vocation:
            The vocation filter to use. No filter used by default.
        page:
            The page to fetch, by default the first page is fetched.
        battleye_type:
            The type of BattlEye protection to display results from.
        pvp_types:
            The list of PvP types to filter the results for.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Highscores]]
            The highscores information or :obj:`None` if not found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If an invalid filter combination is passed or an invalid page is provided.
        """
        pvp_types = pvp_types or []
        if page < 1:
            raise ValueError("page must be 1 or higher.")

        if world is not None and ((battleye_type and battleye_type != HighscoresBattlEyeType.ANY_WORLD) or pvp_types):
            raise ValueError("BattleEye and PvP type filters can only be used when fetching all worlds.")

        response = await self._request("GET", get_highscores_url(world, category,
                                                                 vocation, page, battleye_type,
                                                                 pvp_types), test=test)
        return response.parse(HighscoresParser.from_content)

    async def fetch_leaderboard(
            self,
            world: str,
            rotation: int = None,
            page: int = 1,
            *, test: bool = False,
    ) -> TibiaResponse[Optional[Leaderboard]]:
        """Fetch the leaderboards for a specific world and rotation.

        .. versionadded:: 5.0.0

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        rotation: :class:`int`
            The ID of the rotation. By default, it will get the current rotation.
        page: :class:`int`
            The page to get.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Leaderboard]]
            The leaderboards of the world if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_leaderboards_url(world, rotation, page), test=test)
        return response.parse(LeaderboardParser.from_content)

    async def fetch_kill_statistics(
            self,
            world: str,
            *,
            test: bool = False,
    ) -> TibiaResponse[Optional[KillStatistics]]:
        """Fetch the kill statistics of a world from Tibia.com.

        Parameters
        ----------
        world:
            The name of the world.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[KillStatistics]]
            The kill statistics of the world if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_kill_statistics_url(world), test=test)
        return response.parse(KillStatisticsParser.from_content)

    async def fetch_houses_section(
            self,
            world: str,
            town: str,
            house_type: HouseType = HouseType.HOUSE,
            status: Optional[HouseStatus] = None,
            order: Optional[HouseOrder] = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[HousesSection]:
        """Fetch the house list of a world and type.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`HousesSection` instead.

        Parameters
        ----------
        world:
            The name of the world.
        town:
            The name of the town.
        house_type:
            The type of building. House by default.
        status:
            The house status to filter results. By default, no filters will be applied.
        order:
            The ordering to use for the results. By default, they are sorted by name.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[HousesSection]
            A response containing the lists of houses meeting the criteria if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_houses_section_url(world=world, town=town, house_type=house_type,
                                                                     status=status, order=order), test=test)
        return response.parse(HousesSectionParser.from_content)

    async def fetch_house(self, house_id: int, world: str, *, test: bool = False) -> TibiaResponse[Optional[House]]:
        """Fetch a house in a specific world by its id.

        Parameters
        ----------
        house_id:
            The house's internal id.
        world:
            The name of the world to look for.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[House]]
            The house if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_house_url(world, house_id), test=test)
        return response.parse(HouseParser.from_content)

    async def fetch_world_guilds(self, world: str, *, test: bool = False) -> TibiaResponse[GuildsSection]:
        """Fetch the list of guilds in a world from Tibia.com.

        If a world that does not exist is passed, the world attribute of the result will be :obj:`None`.
        If the world attribute is set, but the list is empty, it just means the world has no guilds.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`GuildsSection` instead.

        Parameters
        ----------
        world:
            The name of the world.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[GuildsSection]
            A response containing the guilds section for the specified world.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_world_guilds_url(world), test=test)
        return response.parse(GuildsSectionParser.from_content)

    async def fetch_guild(self, name: str, *, test: bool = False) -> TibiaResponse[Optional[Guild]]:
        """Fetch a guild by its name from Tibia.com.

        Parameters
        ----------
        name:
            The name of the guild. The case must match exactly.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Guild]]
            A response containing the found guild, if any.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_guild_url(name), test=test)
        return response.parse(GuildParser.from_content)

    async def fetch_guild_wars(self, name: str, *, test: bool = False) -> TibiaResponse[Optional[GuildWars]]:
        """Fetch a guild's wars by its name from Tibia.com.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        name:
            The name of the guild. The case must match exactly.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[GuildWars]]
            A response containing the found guild's wars.

            If the guild doesn't exist, the displayed data will show a guild with no wars instead of indicating the
            guild doesn't exist.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_guild_wars_url(name), test=test)
        return response.parse(GuildWarsParser.from_content)

    async def fetch_fansites_section(self, *, test: bool = False) -> TibiaResponse[FansitesSection]:
        """Fetch the fansites section from Tibia.com.

        .. versionadded:: 6.2.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[FansitesSection]
            A response containing the fansites section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_fansites_url(), test=test)
        return response.parse(FansitesSectionParser.from_content)

    # endregion

    # region Forums
    async def fetch_forum_section(
            self,
            section_id: int,
            *,
            test: bool = False,
    ) -> TibiaResponse[Optional[ForumSection]]:
        """Fetch a forum's section by its ID.

        Parameters
        ----------
        section_id:
            The ID of the section.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumSection]]
            The forum section with the provided ID.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_forum_section_url(section_id), test=test)
        return response.parse(ForumSectionParser.from_content)

    async def fetch_forum_world_boards(self, *, test: bool = False) -> TibiaResponse[Optional[ForumSection]]:
        """Fetch the forum's world boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumSection]]
            The forum boards in the world section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_world_boards_url(), test=test)
        return response.parse(ForumSectionParser.from_content)

    async def fetch_forum_trade_boards(self, *, test: bool = False) -> TibiaResponse[Optional[ForumSection]]:
        """Fetch the forum's trade boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumSection]]
            The forum boards in the trade section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_trade_boards_url(), test=test)
        return response.parse(ForumSectionParser.from_content)

    async def fetch_forum_community_boards(self, *, test: bool = False) -> TibiaResponse[Optional[ForumSection]]:
        """Fetch the forum's community boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumSection]]
            The forum boards in the community section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_community_boards_url(), test=test)
        return response.parse(ForumSectionParser.from_content)

    async def fetch_forum_support_boards(self, *, test: bool = False) -> TibiaResponse[Optional[ForumSection]]:
        """Fetch the forum's community boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumSection]]
            The forum boards in the community section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_support_boards_url(), test=test)
        return response.parse(ForumSectionParser.from_content)

    async def fetch_forum_board(self, board_id: int, page: int = 1, age: int = None, *,
                                test: bool = False) -> TibiaResponse[Optional[ForumBoard]]:
        """Fetch a forum board with a given id.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        board_id
            The id of the board.
        page:
            The page number to show.
        age:
            The maximum age in days of the threads to display.

            To show threads of all ages, use -1.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[ForumBoard]
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_forum_board_url(board_id, page, age), test=test)
        return response.parse(ForumBoardParser.from_content)

    async def fetch_forum_thread(self, thread_id: int, page: int = 1, *,
                                 test: bool = False) -> TibiaResponse[Optional[ForumThread]]:
        """Fetch a forum thread with a given id.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        thread_id:
            The id of the thread.
        page:
            The desired page to display, by default 1.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumThread]]
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_forum_thread_url(thread_id, page), test=test)
        return response.parse(ForumThreadParser.from_content)

    async def fetch_forum_post(self, post_id: int, *, test: bool = False) -> TibiaResponse[Optional[ForumThread]]:
        """Fetch a forum post with a given id.

        The thread that contains the post will be returned, containing the desired post in
        :py:attr:`ForumThread.anchored_post`.

        The displayed page will be the page where the post is located.

        .. versionadded:: 3.1.0

        Parameters
        ----------
        post_id:
            The id of the post.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumThread]]
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_forum_post_url(post_id), test=test)
        built_response = response.parse(ForumThreadParser.from_content)
        if built_response.data is None:
            return built_response

        built_response.data.anchored_post = next((p for p in built_response.data.entries if p.post_id == post_id), None)
        return built_response

    async def fetch_forum_announcement(
            self,
            announcement_id: int,
            *,
            test: bool = False,
    ) -> TibiaResponse[Optional[ForumAnnouncement]]:
        """Fetch a forum announcement.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        announcement_id:
            The id of the desired announcement.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[ForumAnnouncement]]
            The forum announcement, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", get_forum_announcement_url(announcement_id), test=test)
        return response.parse(lambda c: ForumAnnouncementParser.from_content(c, announcement_id))

    async def fetch_cm_post_archive(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            page: int = 1,
            *,
            test: bool = False,
    ) -> TibiaResponse[CMPostArchive]:
        """Fetch the CM post archive.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        start_date:
            The start date to display.
        end_date:
            The end date to display.
        page:
            The desired page to display.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[CMPostArchive]
            The CM Post Archive.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If the start_date is more recent than the end date or page number is not 1 or greater.
        """
        if start_date > end_date:
            raise ValueError("start_date cannot be more recent than end_date")

        if page <= 0:
            raise ValueError("page cannot be lower than 1.")

        response = await self._request("GET", get_cm_post_archive_url(start_date, end_date, page), test=test)
        return response.parse(CMPostArchiveParser.from_content)

    # endregion

    # region Char Bazaar
    async def fetch_current_auctions(
            self,
            page: int = 1,
            filters: Optional[AuctionFilters] = None,
            *,
            test: bool = False,
    ) -> TibiaResponse[CharacterBazaar]:
        """Fetch the current auctions in the bazaar.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        page:
            The desired page to display.
        filters:
            The filtering criteria to use.
        test:
            Whether to fetch from the test website or not.

        Returns
        -------
        TibiaResponse[CharacterBazaar]
            The current auctions.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If the page number is not 1 or greater.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater.")

        response = await self._request("GET", get_bazaar_url(BazaarType.CURRENT, page, filters), test=test)
        return response.parse(CharacterBazaarParser.from_content)

    async def fetch_auction_history(self, page: int = 1, filters: Optional[AuctionFilters] = None, *,
                                    test: bool = False) -> TibiaResponse[CharacterBazaar]:
        """Fetch the auction history of the bazaar.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        page:
            The page to display.
        filters:
            The filtering criteria to use.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[CharacterBazaar]
            The character bazaar containing the auction history.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If the page number is not 1 or greater.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater.")

        response = await self._request("GET", get_bazaar_url(BazaarType.HISTORY, page, filters), test=test)
        return response.parse(CharacterBazaarParser.from_content)

    async def fetch_auction(
            self,
            auction_id: int,
            *,
            fetch_items: bool = False,
            fetch_mounts: bool = False,
            fetch_outfits: bool = False,
            fetch_familiars: bool = False,
            skip_details: bool = False,
            test: bool = False,
    ) -> TibiaResponse[Optional[Auction]]:
        """Fetch an auction by its ID.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        auction_id:
            The ID of the auction.
        fetch_items:
            Whether to fetch all the character's items. By default, only the first page is fetched.
        fetch_mounts:
            Whether to fetch all the character's mounts. By default, only the first page is fetched.
        fetch_outfits:
            Whether to fetch all the character's outfits. By default, only the first page is fetched.
        fetch_familiars:
            Whether to fetch all the character's outfits. By default, only the first page is fetched.
        skip_details:
            Whether to skip parsing the entire auction and only parse the information shown in lists. False by default.

            This allows fetching basic information like name, level, vocation, world, bid and status, shaving off some
            parsing time.
        test:
            Whether to request the test website instead.

        Returns
        -------
        TibiaResponse[Optional[Auction]]
            The auction matching the ID if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If the auction id is not 1 or greater.
        """
        if auction_id <= 0:
            raise ValueError("auction_id must be 1 or greater.")

        response = await self._request("GET", get_auction_url(auction_id), test=test)
        tibia_response = response.parse(lambda c: AuctionParser.from_content(c, auction_id, skip_details))
        if tibia_response.data is None:
            return tibia_response

        auction = tibia_response.data
        if auction and not skip_details:
            if fetch_items:
                await self._fetch_all_pages(auction_id, auction.details.items, 0, test=test)
                await self._fetch_all_pages(auction_id, auction.details.store_items, 1, test=test)

            if fetch_mounts:
                await self._fetch_all_pages(auction_id, auction.details.mounts, 2, test=test)
                await self._fetch_all_pages(auction_id, auction.details.store_mounts, 3, test=test)

            if fetch_outfits:
                await self._fetch_all_pages(auction_id, auction.details.outfits, 4, test=test)
                await self._fetch_all_pages(auction_id, auction.details.store_outfits, 5, test=test)

            if fetch_familiars:
                await self._fetch_all_pages(auction_id, auction.details.outfits, 6, test=test)

        return tibia_response

    # endregion
