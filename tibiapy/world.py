"""Models related to the worlds section in Tibia.com."""
import re
from collections import OrderedDict
from typing import List, TYPE_CHECKING

from tibiapy import abc
from tibiapy.character import OnlineCharacter
from tibiapy.enums import BattlEyeType, PvpType, TournamentWorldType, TransferType, WorldLocation
from tibiapy.errors import InvalidContent
from tibiapy.utils import (get_tibia_url, parse_integer, parse_tibia_datetime, parse_tibia_full_date,
                           parse_tibiacom_content, try_date, try_datetime, try_enum)

if TYPE_CHECKING:
    import bs4

__all__ = (
    "WorldEntry",
    "World",
    "WorldOverview",
)

record_regexp = re.compile(r'(?P<count>[\d.,]+) players \(on (?P<date>[^)]+)\)')
battleye_regexp = re.compile(r'since ([^.]+).')


class WorldEntry(abc.BaseWorld, abc.Serializable):
    """Represents a game server listed in the World Overview section.

    Attributes
    ----------
    name: :class:`str`
        The name of the world.
    status: :class:`str`
        The current status of the world.
    online_count: :class:`int`
        The number of currently online players in the world.
    location: :class:`WorldLocation`
        The physical location of the game servers.
    pvp_type: :class:`PvpType`
        The type of PvP in the world.
    transfer_type: :class:`TransferType`
        The type of transfer restrictions this world has.
    battleye_date: :class:`datetime.date`
        The date when BattlEye was added to this world.
        If this is :obj:`None` and the world is protected, it means the world was protected from the beginning.
    battleye_type: :class:`BattlEyeType`
        The type of BattlEye protection this world has.

        .. versionadded:: 4.0.0
    experimental: :class:`bool`
        Whether the world is experimental or not.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    tournament_world_type: :class:`TournamentWorldType`
        The type of tournament world. :obj:`None` if this is not a tournament world.
    """

    __slots__ = (
        "name",
        "status",
        "location",
        "online_count",
        "pvp_type",
        "battleye_date",
        "battleye_type",
        "experimental",
        "premium_only",
        "tournament_world_type",
        "transfer_type",
    )

    _serializable_properties = (
        "battleye_protected",
    )

    def __init__(self, name, location=None, pvp_type=None, **kwargs):
        self.name: str = name
        self.location = try_enum(WorldLocation, location)
        self.pvp_type = try_enum(PvpType, pvp_type)
        self.status: str = kwargs.get("status")
        self.online_count: int = kwargs.get("online_count", 0)
        self.transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self.battleye_date = try_date(kwargs.get("battleye_date"))
        self.battleye_type = try_enum(BattlEyeType, kwargs.get("battleye_type"), BattlEyeType.UNPROTECTED)
        self.experimental: bool = kwargs.get("experimental", False)
        self.premium_only: bool = kwargs.get("premium_only", False)
        self.tournament_world_type = try_enum(TournamentWorldType, kwargs.get("tournament_world_type"), None)

    @property
    def battleye_protected(self):
        """:class:`bool`: Whether the server is currently protected with BattlEye or not.

        .. versionchanged:: 4.0.0
            Now a calculated property instead of a field.
        """
        return self.battleye_type and self.battleye_type != BattlEyeType.UNPROTECTED

    # region Public methods
    @classmethod
    def get_list_url(cls):
        """Get the URL to the World Overview page in Tibia.com.

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return WorldOverview.get_url()

    @classmethod
    def list_from_content(cls, content):
        """Parse the content of the World Overview section from Tibia.com and returns only the list of worlds.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`list` of :class:`WorldEntry`
            A list of the worlds and their current information.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the worlds section in Tibia.com
        """
        world_overview = WorldOverview.from_content(content)
        return world_overview.worlds

    # endregion

    # region Private methods
    def _parse_additional_info(self, additional_info, tournament=False):
        if "blocked" in additional_info:
            self.transfer_type = TransferType.BLOCKED
        elif "locked" in additional_info:
            self.transfer_type = TransferType.LOCKED
        else:
            self.transfer_type = TransferType.REGULAR
        self.experimental = "experimental" in additional_info
        self.premium_only = "premium" in additional_info
        if tournament:
            if "restricted Store products" in additional_info:
                self.tournament_world_type = TournamentWorldType.RESTRICTED
            else:
                self.tournament_world_type = TournamentWorldType.REGULAR
    # endregion


class World(abc.BaseWorld, abc.Serializable):
    """Represents a Tibia game server.

    Attributes
    ----------
    name: :class:`str`
        The name of the world.
    status: :class:`str`
        The current status of the world.
    online_count: :class:`int`
        The number of currently online players in the world.
    record_count: :class:`int`
        The server's online players record.
    record_date: :class:`datetime.datetime`
        The date when the online record was achieved.
    location: :class:`WorldLocation`
        The physical location of the game servers.
    pvp_type: :class:`PvpType`
        The type of PvP in the world.
    creation_date: :class:`str`
        The month and year the world was created. In YYYY-MM format.
    transfer_type: :class:`TransferType`
        The type of transfer restrictions this world has.
    world_quest_titles: :obj:`list` of :class:`str`
        List of world quest titles the server has achieved.
    battleye_date: :class:`datetime.date`
        The date when BattlEye was added to this world.
        If this is :obj:`None` and the world is protected, it means the world was protected from the beginning.
    battleye_type: :class:`BattlEyeType`
        The type of BattlEye protection this world has.

        .. versionadded:: 4.0.0
    experimental: :class:`bool`
        Whether the world is experimental or not.
    tournament_world_type: :class:`TournamentWorldType`
        The type of tournament world. :obj:`None` if this is not a tournament world.
    online_players: :obj:`list` of :class:`OnlineCharacter`.
        A list of characters currently online in the server.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    """

    __slots__ = (
        "name",
        "status",
        "location",
        "pvp_type",
        "battleye_date",
        "battleye_type",
        "experimental",
        "premium_only",
        "tournament_world_type",
        "transfer_type",
        "online_count",
        "record_count",
        "record_date",
        "creation_date",
        "world_quest_titles",
        "online_players",
    )

    _serializable_properties = (
        "battleye_protected",
    )

    def __init__(self, name, location=None, pvp_type=None, **kwargs):
        self.name: str = name
        self.location = try_enum(WorldLocation, location)
        self.pvp_type = try_enum(PvpType, pvp_type)
        self.status: bool = kwargs.get("status")
        self.online_count: int = kwargs.get("online_count", 0)
        self.record_count: int = kwargs.get("record_count", 0)
        self.record_date = try_datetime(kwargs.get("record_date"))
        self.creation_date: str = kwargs.get("creation_date")
        self.transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self.world_quest_titles: List[str] = kwargs.get("world_quest_titles", [])
        self.battleye_date = try_date(kwargs.get("battleye_date"))
        self.battleye_type = try_enum(BattlEyeType, kwargs.get("battleye_type"), BattlEyeType.UNPROTECTED)
        self.experimental: bool = kwargs.get("experimental", False)
        self.online_players: List[OnlineCharacter] = kwargs.get("online_players", [])
        self.premium_only: bool = kwargs.get("premium_only", False)
        self.tournament_world_type = try_enum(TournamentWorldType, kwargs.get("tournament_world_type"), None)

    # region Properties
    @property
    def battleye_protected(self):
        """:class:`bool`: Whether the server is currently protected with BattlEye or not.

        .. versionchanged:: 4.0.0
            Now a calculated property instead of a field.
        """
        return self.battleye_type and self.battleye_type != BattlEyeType.UNPROTECTED

    @property
    def creation_year(self):
        """:class:`int`: Returns the year when the world was created."""
        return int(self.creation_date.split("-")[0]) if self.creation_date else None

    @property
    def creation_month(self):
        """:class:`int`: Returns the month when the world was created."""
        return int(self.creation_date.split("-")[1])if self.creation_date else None
    # endregion

    # region Public methods
    @classmethod
    def from_content(cls, content):
        """Parse a Tibia.com response into a :class:`World`.

        Parameters
        ----------
        content: :class:`str`
            The raw HTML from the server's information page.

        Returns
        -------
        :class:`World`
            The World described in the page, or :obj:`None`.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the world section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        try:
            error = tables.get("Error")
            if error and error[0].text == "World with this name doesn't exist!":
                return None
            selected_world = parsed_content.select_one('option:checked')
            world = cls(selected_world.text)
            world._parse_world_info(tables.get("World Information", []))

            online_table = tables.get("Players Online", [])
            world.online_players = []
            for row in online_table[1:]:
                cols_raw = row.select('td')
                name, level, vocation = (c.text.replace('\xa0', ' ').strip() for c in cols_raw)
                world.online_players.append(OnlineCharacter(name, world.name, int(level), vocation))
        except AttributeError:
            raise InvalidContent("content is not from the world section in Tibia.com")

        return world
    # endregion

    # region Private methods
    def _parse_world_info(self, world_info_table):
        """
        Parse the World Information table from Tibia.com and adds the found values to the object.

        Parameters
        ----------
        world_info_table: :class:`list`[:class:`bs4.Tag`]
        """
        world_info = {}
        for row in world_info_table:
            cols_raw = row.select('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            world_info[field] = value
        try:
            self.online_count = parse_integer(world_info.pop("players_online"))
        except KeyError:
            self.online_count = 0
        self.location = try_enum(WorldLocation, world_info.pop("location"))
        self.pvp_type = try_enum(PvpType, world_info.pop("pvp_type"))
        self.transfer_type = try_enum(TransferType, world_info.pop("transfer_type", None), TransferType.REGULAR)
        m = record_regexp.match(world_info.pop("online_record"))
        if m:
            self.record_count = parse_integer(m.group("count"))
            self.record_date = parse_tibia_datetime(m.group("date"))
        if "world_quest_titles" in world_info:
            self.world_quest_titles = [q.strip() for q in world_info.pop("world_quest_titles").split(",")]
        if self.world_quest_titles and "currently has no title" in self.world_quest_titles[0]:
            self.world_quest_titles = []
        self.experimental = world_info.pop("game_world_type", None) == "Experimental"
        self.tournament_world_type = try_enum(TournamentWorldType, world_info.pop("tournament_world_type", None))
        self._parse_battleye_status(world_info.pop("battleye_status"))
        self.premium_only = "premium_type" in world_info

        month, year = world_info.pop("creation_date").split("/")
        month = int(month)
        year = int(year)
        if year > 90:
            year += 1900
        else:
            year += 2000
        self.creation_date = f"{year:d}-{month:02d}"

        for k, v in world_info.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    def _parse_battleye_status(self, battleye_string):
        """Parse the BattlEye string and applies the results.

        Parameters
        ----------
        battleye_string: :class:`str`
            String containing the world's Battleye Status.
        """
        m = battleye_regexp.search(battleye_string)
        if m:
            self.battleye_date = parse_tibia_full_date(m.group(1))
            self.battleye_type = BattlEyeType.PROTECTED if self.battleye_date else BattlEyeType.INITIALLY_PROTECTED
        else:
            self.battleye_date = None
            self.battleye_type = BattlEyeType.UNPROTECTED

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parse the information tables found in a world's information page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[:class:`str`, :class:`list`[:class:`bs4.Tag`]]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.select('div.TableContainer')
        output = OrderedDict()
        for table in tables:
            title = table.select_one("div.Text").text
            title = title.split("[")[0].strip()
            inner_table = table.select_one("div.InnerTableContainer")
            output[title] = inner_table.select("tr")
        return output
    # endregion


class WorldOverview(abc.Serializable):
    """Container class for the World Overview section.

    Attributes
    ----------
    record_count: :class:`int`
        The overall player online record.
    record_date: :class:`datetime.datetime`
        The date when the record was achieved.
    worlds: :class:`list` of :class:`WorldEntry`
        List of worlds, with limited info.
    """

    __slots__ = (
        "record_count",
        "record_date",
        "worlds",
    )

    serializable_properties = ('total_online',)

    def __init__(self, **kwargs):
        self.record_count: int = kwargs.get("record_count", 0)
        self.record_date = try_datetime(kwargs.get("record_date"))
        self.worlds: List[WorldEntry] = kwargs.get("worlds", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} total_online={self.total_online:d}>"

    @property
    def total_online(self):
        """:class:`int`: Total players online across all worlds."""
        return sum(w.online_count for w in self.worlds)

    @property
    def tournament_worlds(self):
        """:class:`list` of :class:`GuildMember`: List of tournament worlds.

        Note that tournament worlds are not listed when there are no active or upcoming tournaments.
        """
        return [w for w in self.worlds if w.tournament_world_type is not None]

    @property
    def regular_worlds(self):
        """:class:`list` of :class:`WorldEntry`: List of worlds that are not tournament worlds."""
        return [w for w in self.worlds if w.tournament_world_type is None]

    @classmethod
    def get_url(cls):
        """Get the URL to the World Overview page in Tibia.com.

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return get_tibia_url("community", "worlds")

    @classmethod
    def from_content(cls, content):
        """Parse the content of the World Overview section from Tibia.com into an object of this class.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`WorldOverview`
            An instance of this class containing all the information.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the worlds section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        world_overview = WorldOverview()
        try:
            record_table, *tables \
                = parsed_content.select("table.TableContent")
            m = record_regexp.search(record_table.text)
            world_overview.record_count = parse_integer(m.group("count"))
            world_overview.record_date = parse_tibia_datetime(m.group("date"))
            world_overview._parse_worlds_tables(tables)
            return world_overview
        except (AttributeError, KeyError, ValueError) as e:
            raise InvalidContent("content does not belong to the World Overview section in Tibia.com", e)

    def _parse_worlds(self, world_rows, tournament=False):
        """Parse the world columns and adds the results to :py:attr:`worlds`.

        Parameters
        ----------
        world_rows: :class:`list` of :class:`bs4.Tag`
            A list containing the rows of each world.
        tournament: :class:`bool`
            Whether these are tournament worlds or not.
        """
        for world_row in world_rows:
            cols = world_row.select("td")
            name = cols[0].text.strip()
            status = "Online"
            online = parse_integer(cols[1].text.strip(), None)
            if online is None:
                online = 0
                status = "Offline"
            location = cols[2].text.replace("\u00a0", " ").strip()
            pvp = cols[3].text.strip()

            world = WorldEntry(name, location, pvp, online_count=online, status=status)
            # Check Battleye icon to get information
            battleye_icon = cols[4].select_one("span.HelperDivIndicator")
            if battleye_icon is not None:
                m = battleye_regexp.search(battleye_icon["onmouseover"])
                if m:
                    world.battleye_date = parse_tibia_full_date(m.group(1))
                    world.battleye_type = BattlEyeType.PROTECTED if world.battleye_date else BattlEyeType.INITIALLY_PROTECTED
            additional_info = cols[5].text.strip()
            world._parse_additional_info(additional_info, tournament)
            self.worlds.append(world)

    def _parse_worlds_tables(self, tables):
        """Parse the tables and adds the results to the world list.

        Parameters
        ----------
        tables: :class:`map` of :class:`bs4.Tag`
            A mapping containing the tables with worlds.
        """
        for title_table, worlds_table in zip(tables, tables[1:]):
            title = title_table.text.lower()
            regular_world_rows = worlds_table.select("tr.Odd, tr.Even")
            self._parse_worlds(regular_world_rows, "tournament" in title)
