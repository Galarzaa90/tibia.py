"""Asynchronous Tibia.com client."""
import asyncio
import datetime
import json
import logging
import time
import typing

import aiohttp
import aiohttp_socks

import tibiapy
from tibiapy import Auction, AuctionFilters, CharacterBazaar, Leaderboard, Spell, SpellsSection, abc
from tibiapy.character import Character
from tibiapy.creature import BoostableBosses, BoostedCreatures, Creature, CreatureEntry, CreaturesSection
from tibiapy.enums import BattlEyeHighscoresFilter, Category, HouseType, NewsCategory, \
    NewsType, VocationFilter
from tibiapy.errors import Forbidden, NetworkError, SiteMaintenanceError
from tibiapy.event import EventSchedule
from tibiapy.forum import BoardEntry, CMPostArchive, ForumAnnouncement, ForumBoard, ForumPost, ForumThread
from tibiapy.guild import Guild, GuildWars, GuildsSection
from tibiapy.highscores import Highscores
from tibiapy.house import House, HousesSection
from tibiapy.kill_statistics import KillStatistics
from tibiapy.news import News, NewsArchive
from tibiapy.tournament import Tournament, TournamentLeaderboard
from tibiapy.world import World, WorldOverview

__all__ = (
    "TibiaResponse",
    "Client",
)

# Tibia.com's cache for the community section is 5 minutes.
# This limit is not sent anywhere, so there's no way to automate it.
CACHE_LIMIT = 300

T = typing.TypeVar('T')

log = logging.getLogger("tibiapy")


class TibiaResponse(typing.Generic[T], abc.Serializable):
    """Represents a response from Tibia.com.

    Attributes
    ----------
    timestamp: :class:`datetime.datetime`
        The date and time when the page was fetched, in UTC.
    cached: :class:`bool`
        Whether the response is cached or it is a fresh response.
    age: :class:`int`
        The age of the cache in seconds.
    fetching_time: :class:`float`
        The time in seconds it took for Tibia.com to respond.
    parsing_time: :class:`float`
        The time in seconds it took for the response to be parsed into data.
    data: :class:`T`
        The data contained in the response.
    """

    def __init__(self, raw_response, data: T, parsing_time=None):
        self.timestamp: datetime.datetime = raw_response.timestamp
        self.cached: bool = raw_response.cached
        self.age: int = raw_response.age
        self.fetching_time = raw_response.fetching_time
        self.parsing_time = parsing_time
        self.data: T = data

    __slots__ = (
        'timestamp',
        'cached',
        'age',
        'fetching_time',
        'parsing_time',
        'data',
    )

    _serializable_properties = ("time_left", )

    def __repr__(self):
        return f"<{self.__class__.__name__}[{type(self.data).__name__}] timestamp={self.timestamp!r} " \
               f"fetching_time={self.fetching_time!r} parsing_time={self.fetching_time!r} cahed={self.cached!r} " \
               f"age={self.age!r}>"

    @property
    def time_left(self):
        """:class:`datetime.timedelta`: The time left for the cache of this response to expire."""
        if not self.age:
            return datetime.timedelta()
        return (datetime.timedelta(seconds=CACHE_LIMIT - self.age)
                - (datetime.datetime.now(datetime.timezone.utc) - self.timestamp))

    @property
    def seconds_left(self):
        """:class:`int`: The time left in seconds for this response's cache to expire."""
        return self.time_left.seconds


class RawResponse:
    def __init__(self, response: aiohttp.ClientResponse, fetching_time: float):
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.fetching_time = fetching_time
        self.cached = response.headers.get("CF-Cache-Status") == "HIT"
        age = response.headers.get("Age")
        if age is not None and age.isnumeric():
            self.age = int(age)
        else:
            self.age = 0
        self.content = None

    def __repr__(self):
        return f"<{self.__class__.__name__} timestamp={self.timestamp!r} fetching_time={self.fetching_time!r} " \
               f"cached={self.cached!r} age={self.age!r}>"


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

    def __init__(self, loop=None, session=None, *, proxy_url=None):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        self._session_ready = asyncio.Event()
        if session is not None:
            self.session: aiohttp.ClientSession = session
            self._session_ready.set()
        else:
            self.loop.create_task(self._initialize_session(proxy_url))

    # region Private Methods

    async def _initialize_session(self, proxy_url=None):
        """Initialize the aiohttp session object."""
        headers = {
            'User-Agent': "Tibia.py/%s (+https://github.com/Galarzaa90/tibia.py)" % tibiapy.__version__,
            'Accept-Encoding': "deflate, gzip",
        }
        connector = aiohttp_socks.SocksConnector.from_url(proxy_url) if proxy_url else None
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(
            loop=self.loop,
            headers=headers,
            connector=connector,
        )
        self._session_ready.set()

    @classmethod
    def _handle_status(cls, status_code: int, fetching_time=0.0):
        """Handle error status codes, raising exceptions if necessary."""
        if status_code < 400:
            return
        if status_code == 403:
            raise Forbidden("403 Forbidden: Might be getting rate-limited", fetching_time=fetching_time)
        else:
            raise NetworkError("Request error, status code: %d" % status_code, fetching_time=fetching_time)

    async def _request(self, method, url, data=None, headers=None, *, test=False):
        """Base request, handling possible error statuses.

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
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`RawResponse`
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
                diff_time = time.perf_counter()-init_time
                if "maintenance.tibia.com" in str(resp.url):
                    log.info("%s | %s | %s %s | maintenance.tibia.com", url, resp.method, resp.status, resp.reason)
                    raise SiteMaintenanceError("Tibia.com is down for maintenance.")
                log.info("%s | %s | %s %s | %dms", url, resp.method, resp.status, resp.reason, int(diff_time * 1000))
                self._handle_status(resp.status, diff_time)
                response = RawResponse(resp, diff_time)
                response.content = await resp.text()
                return response
        except aiohttp.ClientError as e:
            raise NetworkError(f"aiohttp.ClientError: {e}", e, time.perf_counter() - init_time)
        except aiohttp_socks.SocksConnectionError as e:
            raise NetworkError(f"aiohttp_socks.SocksConnectionError: {e}", e, time.perf_counter() - init_time)
        except UnicodeDecodeError as e:
            raise NetworkError(f'UnicodeDecodeError: {e}', e, time.perf_counter() - init_time)

    async def _fetch_all_pages(self, auction_id, paginator, item_type, *, test=False):
        """Fetch all the pages of an auction paginator.

        Parameters
        ----------
        auction_id: :class:`int`
            The id of the auction.
        paginator:
            The paginator object
        item_type: :class:`int`
            The item type.
        test: :class:`bool`
            Whether to request the test website instead.
        """
        if paginator is None or paginator.entry_class is None:
            return
        current_page = 2
        while current_page <= paginator.total_pages:
            content = await self._fetch_ajax_page(auction_id, item_type, current_page, test=test)
            if content:
                entries = Auction._parse_page_items(content, paginator.entry_class)
                paginator.entries.extend(entries)
            current_page += 1
        paginator.fully_fetched = True

    async def _fetch_ajax_page(self, auction_id, type_id, page, *, test=False):
        """Fetch an ajax page from the paginated summaries in the auction section.

        Parameters
        ----------
        auction_id: :class:`int`
            The id of the auction.
        type_id: :class:`int`
            The ID of the type of the catalog to check.
        page: :class:`int`
            The page number to fetch.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`str`:
            The HTML content of the obtained page.
        """
        headers = {"x-requested-with": "XMLHttpRequest"}
        page_response = await self._request("GET", f"https://www.tibia.com/websiteservices/handle_charactertrades.php?"
                                                   f"auctionid={auction_id}&"
                                                   f"type={type_id}&"
                                                   f"currentpage={page}",
                                            headers=headers,
                                            test=test)
        try:
            data = json.loads(page_response.content.replace("\x0a", " "))
        except json.decoder.JSONDecodeError:
            return None
        try:
            return data['AjaxObjects'][0]['Data']
        except KeyError:
            return None

    # endregion

    # region Bazaar
    async def fetch_current_auctions(self, page=1, filters=None, *, test=False):
        """Fetch the current auctions in the bazaar.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        page: :class:`int`
            The desired page to display.
        filters: :class:`AuctionFilters`
            The filtering criteria to use.

        Returns
        -------
        :class:`TibiaResponse` of :class:`CharacterBazaar`
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
            raise ValueError('page must be 1 or greater.')
        response = await self._request("GET", CharacterBazaar.get_current_auctions_url(page, filters), test=test)
        start_time = time.perf_counter()
        current_auctions = CharacterBazaar.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, current_auctions, parsing_time)

    async def fetch_auction_history(self, page=1, filters=None, *, test=False):
        """Fetch the auction history of the bazaar.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        page: :class:`int`
            The page to display.
        filters: :class:`AuctionFilters`
            The filtering criteria to use.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`CharacterBazaar`
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
            raise ValueError('page must be 1 or greater.')
        response = await self._request("GET", CharacterBazaar.get_auctions_history_url(page, filters), test=test)
        start_time = time.perf_counter()
        auction_history = CharacterBazaar.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, auction_history, parsing_time)

    async def fetch_auction(self, auction_id, *, fetch_items=False, fetch_mounts=False, fetch_outfits=False,
                            skip_details=False, test=False):
        """Fetch an auction by its ID.

        .. versionadded:: 3.3.0

        Parameters
        ----------
        auction_id: :class:`int`
            The ID of the auction.
        fetch_items: :class:`bool`
            Whether to fetch all of the character's items. By default only the first page is fetched.
        fetch_mounts: :class:`bool`
            Whether to fetch all of the character's mounts. By default only the first page is fetched.
        fetch_outfits: :class:`bool`
            Whether to fetch all of the character's outfits. By default only the first page is fetched.
        skip_details: :class:`bool`, optional
            Whether to skip parsing the entire auction and only parse the information shown in lists. False by default.

            This allows fetching basic information like name, level, vocation, world, bid and status, shaving off some
            parsing time.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Auction`
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
            raise ValueError('auction_id must be 1 or greater.')
        response = await self._request("GET", Auction.get_url(auction_id), test=test)
        start_time = time.perf_counter()
        auction = Auction.from_content(response.content, auction_id, skip_details)
        parsing_time = time.perf_counter() - start_time
        if auction and not skip_details:
            if fetch_items:
                await self._fetch_all_pages(auction_id, auction.items, 0, test=test)
                await self._fetch_all_pages(auction_id, auction.store_items, 1, test=test)
            if fetch_mounts:
                await self._fetch_all_pages(auction_id, auction.mounts, 2, test=test)
                await self._fetch_all_pages(auction_id, auction.store_mounts, 3, test=test)
            if fetch_outfits:
                await self._fetch_all_pages(auction_id, auction.outfits, 4, test=test)
                await self._fetch_all_pages(auction_id, auction.store_outfits, 5, test=test)
        return TibiaResponse(response, auction, parsing_time)

    # endregion

    async def fetch_cm_post_archive(self, start_date, end_date, page=1, *, test=False):
        """Fetch the CM post archive.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        start_date: :class: `datetime.date`
            The start date to display.
        end_date: :class: `datetime.date`
            The end date to display.
        page: :class:`int`
            The desired page to display.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`CMPostArchive`
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
        response = await self._request("GET", CMPostArchive.get_url(start_date, end_date, page), test=test)
        start_time = time.perf_counter()
        cm_post_archive = CMPostArchive.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, cm_post_archive, parsing_time)

    async def fetch_event_schedule(self, month=None, year=None, *, test=False):
        """Fetch the event calendar. By default, it gets the events for the current month.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        month: :class:`int`
            The month of the events to display.
        year: :class:`int`
            The year of the events to display.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`EventSchedule`
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
        response = await self._request("GET", EventSchedule.get_url(month, year), test=test)
        start_time = time.perf_counter()
        calendar = EventSchedule.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, calendar, parsing_time)

    # region Forums
    async def fetch_forum_community_boards(self, *, test=False):
        """Fetch the forum's community boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of list of :class:`BoardEntry`
            The forum boards in the community section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", BoardEntry.get_community_boards_url(), test=test)
        start_time = time.perf_counter()
        boards = BoardEntry.list_from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boards, parsing_time)

    async def fetch_forum_support_boards(self, *, test=False):
        """Fetch the forum's community boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of list of :class:`BoardEntry`
            The forum boards in the community section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", BoardEntry.get_support_boards_url(), test=test)
        start_time = time.perf_counter()
        boards = BoardEntry.list_from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boards, parsing_time)

    async def fetch_forum_world_boards(self, *, test=False):
        """Fetch the forum's world boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of list of :class:`BoardEntry`
            The forum boards in the world section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", BoardEntry.get_world_boards_url(), test=test)
        start_time = time.perf_counter()
        boards = BoardEntry.list_from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boards, parsing_time)

    async def fetch_forum_trade_boards(self, *, test=False):
        """Fetch the forum's trade boards.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of list of :class:`BoardEntry`
            The forum boards in the trade section.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", BoardEntry.get_trade_boards_url(), test=test)
        start_time = time.perf_counter()
        boards = BoardEntry.list_from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boards, parsing_time)

    async def fetch_forum_board(self, board_id, page=1, age=30, *, test=False):
        """Fetch a forum board with a given id.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        board_id : :class:`int`
            The id of the board.
        page: :class:`int`
            The page number to show.
        age: :class:`int`
            The maximum age in days of the threads to display.

            To show threads of all ages, use -1.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`ForumBoard`
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", ForumBoard.get_url(board_id, page, age), test=test)
        start_time = time.perf_counter()
        board = ForumBoard.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, board, parsing_time)

    async def fetch_forum_thread(self, thread_id, page=1, *, test=False):
        """Fetch a forum thread with a given id.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        thread_id : :class:`int`
            The id of the thread.
        page: :class:`int`
            The desired page to display, by default 1.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`ForumThread`
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", ForumThread.get_url(thread_id, page), test=test)
        start_time = time.perf_counter()
        thread = ForumThread.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, thread, parsing_time)

    async def fetch_forum_post(self, post_id, *, test=False):
        """Fetch a forum post with a given id.

        The thread that contains the post will be returned, containing the desired post in
        :py:attr:`ForumThread.anchored_post`.

        The displayed page will be the page where the post is located.

        .. versionadded:: 3.1.0

        Parameters
        ----------
        post_id : :class:`int`
            The id of the post.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`ForumThread`
            A response containing the forum, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", ForumPost.get_url(post_id), test=test)
        start_time = time.perf_counter()
        thread = ForumThread.from_content(response.content)
        if thread:
            thread.anchored_post = next((p for p in thread.posts if p.post_id == post_id), None)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, thread, parsing_time)

    async def fetch_forum_announcement(self, announcement_id, *, test=False):
        """Fetch a forum announcement.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        announcement_id: :class:`int`
            The id of the desired announcement.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`ForumAnnouncement`
            The forum announcement, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", ForumAnnouncement.get_url(announcement_id), test=test)
        start_time = time.perf_counter()
        announcement = ForumAnnouncement.from_content(response.content, announcement_id)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, announcement, parsing_time)

    # endregion

    async def fetch_boosted_creature_and_boss(self, *, test=False):
        """Fetch today's boosted creature and boss.

        .. versionadded:: 5.3.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`BoostedCreatures`
            The boosted creature and boss of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", NewsArchive.get_url(), test=test)
        start_time = time.perf_counter()
        boosted_creatures = BoostedCreatures.from_header(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creatures, parsing_time)

    # Region Bosses
    async def fetch_boosted_boss(self, *, test=False):
        """Fetch today's boosted boss.

        .. versionadded:: 5.3.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`BossEntry`
            The boosted boss of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", NewsArchive.get_url(), test=test)
        start_time = time.perf_counter()
        boosted_creature = BoostableBosses.boosted_boss_from_header(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creature, parsing_time)

    async def fetch_library_bosses(self, *, test=False):
        """Fetch the bosses from the library section.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`BoostableBosses`
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", BoostableBosses.get_url(), test=test)
        start_time = time.perf_counter()
        boosted_creature = BoostableBosses.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creature, parsing_time)

    # endregion

    # region Creatures
    async def fetch_boosted_creature(self, *, test=False):
        """Fetch today's boosted creature.

        .. versionadded:: 2.1.0
        .. versionchanged:: 4.0.0
            The return type of the data returned was changed to :class:`Creature`, previous type was removed.

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`CreatureEntry`
            The boosted creature of the day.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", NewsArchive.get_url(), test=test)
        start_time = time.perf_counter()
        boosted_creature = CreaturesSection.boosted_creature_from_header(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creature, parsing_time)

    async def fetch_library_creatures(self, *, test=False):
        """Fetch the creatures from the library section.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`CreaturesSection`
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", CreaturesSection.get_url(), test=test)
        start_time = time.perf_counter()
        boosted_creature = CreaturesSection.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creature, parsing_time)

    async def fetch_creature(self, identifier, *, test=False):
        """Fetch a creature's information from the Tibia.com library.

        .. versionadded:: 4.0.0

        Parameters
        ----------
        identifier: :class:`str`
            The internal name of the race.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Creature`
            The creature's section in Tibia.com

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Creature.get_url(identifier), test=test)
        start_time = time.perf_counter()
        boosted_creature = Creature.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, boosted_creature, parsing_time)

    # endregion

    async def fetch_character(self, name, *, test=False):
        """Fetch a character by its name from Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the character.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Character`
            A response containing the character, if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Character.get_url(name.strip()), test=test)
        start_time = time.perf_counter()
        char = Character.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, char, parsing_time)

    # region Guilds
    async def fetch_guild(self, name, *, test=False):
        """Fetch a guild by its name from Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild. The case must match exactly.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Guild`
            A response containing the found guild, if any.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Guild.get_url(name), test=test)
        start_time = time.perf_counter()
        guild = Guild.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, guild, parsing_time)

    async def fetch_guild_wars(self, name, *, test=False):
        """Fetch a guild's wars by its name from Tibia.com.

        .. versionadded:: 3.0.0

        Parameters
        ----------
        name: :class:`str`
            The name of the guild. The case must match exactly.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`GuildWars`
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
        response = await self._request("GET", GuildWars.get_url(name), test=test)
        start_time = time.perf_counter()
        guild_wars = GuildWars.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, guild_wars, parsing_time)

    # endregion

    async def fetch_house(self, house_id, world, *, test=False):
        """Fetch a house in a specific world by its id.

        Parameters
        ----------
        house_id: :class:`int`
            The house's internal id.
        world: :class:`str`
            The name of the world to look for.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`House`
            The house if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", House.get_url(house_id, world), test=test)
        start_time = time.perf_counter()
        house = House.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, house, parsing_time)

    async def fetch_highscores_page(self, world=None, category=Category.EXPERIENCE, vocation=VocationFilter.ALL, page=1,
                                    battleye_type=None, pvp_types=None, *, test=False):
        """Fetch a single highscores page from Tibia.com.

        Notes
        -----
        It is not possible to use BattlEye or PvPType filters when requesting a specific world.

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
        battleye_type: :class:`BattlEyeFilter`
            The type of BattlEye protection to display results from.
        pvp_types: :class:`list` of :class:`PvpTypeFilter`
            The list of PvP types to filter the results for.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Highscores`
            The highscores information or :obj:`None` if not found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        ValueError
            If an invalid filter combination is passed.
        """
        pvp_types = pvp_types or []
        if world is not None and ((battleye_type and battleye_type != BattlEyeHighscoresFilter.ANY_WORLD) or pvp_types):
            raise ValueError("BattleEye and PvP type filters can only be used when fetching all worlds.")
        response = await self._request("GET", Highscores.get_url(world, category, vocation, page, battleye_type,
                                                                 pvp_types), test=test)
        start_time = time.perf_counter()
        highscores = Highscores.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, highscores, parsing_time)

    async def fetch_kill_statistics(self, world, *, test=False):
        """Fetch the kill statistics of a world from Tibia.com.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`KillStatistics`
            The kill statistics of the world if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", KillStatistics.get_url(world), test=test)
        start_time = time.perf_counter()
        kill_statistics = KillStatistics.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, kill_statistics, parsing_time)

    async def fetch_leaderboard(self, world, rotation=None, page=1, *, test=False):
        """Fetch the leaderboards for a specific world and rotation.

        .. versionadded:: 5.0.0

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        rotation: :class:`int`
            The ID of the rotation. By default it will get the current rotation.
        page: :class:`int`
            The page to get.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Leaderboard`
            The leaderboards of the world if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Leaderboard.get_url(world, rotation, page), test=test)
        start_time = time.perf_counter()
        leaderboard = Leaderboard.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, leaderboard, parsing_time)

    # region Worlds
    async def fetch_world(self, name, *, test=False):
        """Fetch a world from Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`World`
            A response containig the he world's information if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", World.get_url(name), test=test)
        start_time = time.perf_counter()
        world = World.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, world, parsing_time)

    async def fetch_world_houses(self, world, town, house_type=HouseType.HOUSE, status=None, order=None, *, test=False):
        """Fetch the house list of a world and type.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`HousesSection` instead.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        town: :class:`str`
            The name of the town.
        house_type: :class:`HouseType`
            The type of building. House by default.
        status: :class:`HouseStatus`, optional
            The house status to filter results. By default, no filters will be applied.
        order: :class:`HouseOrder`, optional
            The ordering to use for the results. By default, they are sorted by name.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`HousesSection`
            A response containing the lists of houses meeting the criteria if found.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", HousesSection.get_url(world=world, town=town, house_type=house_type,
                                                                    status=status, order=order), test=test)
        start_time = time.perf_counter()
        world_houses = HousesSection.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, world_houses, parsing_time)

    async def fetch_world_guilds(self, world: str, *, test=False):
        """Fetch the list of guilds in a world from Tibia.com.

        If a world that does not exist is passed, the world attribute of the result will be :obj:`None`.
        If the world attribute is set, but the list is empty, it just means the world has no guilds.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`GuildsSection` instead.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`GuildsSection`
            A response containing the guilds section for the specified world.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", GuildsSection.get_url(world), test=test)
        start_time = time.perf_counter()
        guilds = GuildsSection.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, guilds, parsing_time)

    async def fetch_world_list(self, *, test=False):
        """Fetch the world overview information from Tibia.com.

        Parameters
        ----------
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`WorldOverview`
            A response containing the world overview information.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", WorldOverview.get_url(), test=test)
        start_time = time.perf_counter()
        world_overview = WorldOverview.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, world_overview, parsing_time)

    # endregion

    # region News
    async def fetch_news_archive(self, start_date, end_date, categories=None, types=None, *, test=False):
        """Fetch news from the archive meeting the search criteria.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`NewsArchive` instead.

        Parameters
        ----------
        start_date: :class:`datetime.date`
            The beginning date to search dates in.
        end_date: :class:`datetime.date`
            The end date to search dates in.
        categories: `list` of :class:`NewsCategory`
            The allowed categories to show. If left blank, all categories will be searched.
        types : `list` of :class:`NewsType`
            The allowed news types to show. if unused, all types will be searched.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`NewsArchive`
            The news meeting the search criteria.

        Raises
        ------
        ValueError:
            If ``begin_date`` is more recent than ``to_date``.
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        if start_date > end_date:
            raise ValueError("start_date can't be more recent than end_date")
        form_data = NewsArchive.get_form_data(start_date, end_date, categories, types)
        response = await self._request("POST", NewsArchive.get_url(), form_data, test=test)
        start_time = time.perf_counter()
        news = NewsArchive.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, news, parsing_time)

    async def fetch_recent_news(self, days=30, categories=None, types=None, *, test=False):
        """Fetch all the published news in the last specified days.

        This is a shortcut for :meth:`fetch_news_archive`, to handle dates more easily.

        .. versionchanged:: 5.0.0
            The data attribute of the response contains an instance of :class:`NewsArchive` instead.

        Parameters
        ----------
        days: :class:`int`
            The number of days to search, by default 30.
        categories: `list` of :class:`NewsCategory`
            The allowed categories to show. If left blank, all categories will be searched.
        types : `list` of :class:`NewsType`
            The allowed news types to show. if unused, all types will be searched.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`NewsArchive`
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
        return await self.fetch_news_archive(begin, end, categories, types, test=test)

    async def fetch_news(self, news_id, *, test=False):
        """Fetch a news entry by its id from Tibia.com.

        Parameters
        ----------
        news_id: :class:`int`
            The id of the news entry.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`News`
            The news entry if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", News.get_url(news_id), test=test)
        start_time = time.perf_counter()
        news = News.from_content(response.content, news_id)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, news, parsing_time)
    # endregion

    # region Spells
    async def fetch_spells(self, *, vocation=None, group=None, spell_type=None, premium=None, sort=None, test=False):
        """Fetch the spells section.

        Parameters
        ----------
        vocation: :class:`VocationSpellFilter`, optional
            The vocation to filter in spells for.
        group: :class:`SpellGroup`, optional
            The spell's primary cooldown group.
        spell_type: :class:`SpellType`, optional
            The type of spells to show.
        premium: :class:`bool`, optional
            The type of premium requirement to filter. :obj:`None` means any premium requirement.
        sort: :class:`SpellSorting`, optional
            The field to sort spells by.

        Returns
        -------
        :class:`TibiaResponse` of :class:`SpellsSection`
            The spells section with the results.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", SpellsSection.get_url(vocation=vocation, group=group,
                                                                    spell_type=spell_type, premium=premium,
                                                                    sort=sort), test=test)
        start_time = time.perf_counter()
        spells = SpellsSection.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, spells, parsing_time)

    async def fetch_spell(self, identifier, *, test=False):
        """Fetch a spell by its identifier.

        Parameters
        ----------
        identifier: :class:`str`
            The spell's identifier. This is usually the name of the spell in lowercase and with no spaces.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Spell`
            The spell if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Spell.get_url(identifier), test=test)
        start_time = time.perf_counter()
        spells = Spell.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, spells, parsing_time)
    # endregion

    # region Tournaments
    async def fetch_tournament(self, tournament_cycle=0, *, test=False):
        """Fetch a tournament from Tibia.com.

        .. versionadded:: 2.5.0

        Parameters
        ----------
        tournament_cycle: :class:`int`
            The cycle of the tournament. if unspecified, it will get the currently running tournament.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`Tournament`
            The tournament if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", Tournament.get_url(tournament_cycle), test=test)
        start_time = time.perf_counter()
        tournament = Tournament.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, tournament, parsing_time)

    async def fetch_tournament_leaderboard(self, tournament_cycle, world, page=1, *, test=False):
        """Fetch a tournament leaderboard from Tibia.com.

        .. versionadded:: 2.5.0

        Parameters
        ----------
        tournament_cycle: :class:`int`
            The cycle of the tournament. if unspecified, it will get the currently running tournament.
        world: :class:`str`
            The name of the world to get the leaderboards for.
        page: :class:`int`
            The desired leaderboards page, by default 1 is used.
        test: :class:`bool`
            Whether to request the test website instead.

        Returns
        -------
        :class:`TibiaResponse` of :class:`TournamentLeaderboard`
            The tournament's leaderboard if found, :obj:`None` otherwise.

        Raises
        ------
        Forbidden
            If a 403 Forbidden error was returned.
            This usually means that Tibia.com is rate-limiting the client because of too many requests.
        NetworkError
            If there's any connection errors during the request.
        """
        response = await self._request("GET", TournamentLeaderboard.get_url(world, tournament_cycle, page), test=test)
        start_time = time.perf_counter()
        tournament_leaderboard = TournamentLeaderboard.from_content(response.content)
        parsing_time = time.perf_counter() - start_time
        return TibiaResponse(response, tournament_leaderboard, parsing_time)
    # endregion
