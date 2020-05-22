import re
from collections import OrderedDict
from typing import List

import bs4

from tibiapy import InvalidContent, abc, TournamentWorldType
from tibiapy.character import OnlineCharacter
from tibiapy.enums import PvpType, TransferType, WorldLocation
from tibiapy.utils import get_tibia_url, parse_json, parse_tibia_datetime, parse_tibia_full_date, \
    parse_tibiacom_content, \
    parse_tibiadata_datetime, try_date, try_datetime, try_enum, parse_integer

__all__ = (
    "ListedWorld",
    "World",
    "WorldOverview",
)

record_regexp = re.compile(r'(?P<count>[\d.,]+) players \(on (?P<date>[^)]+)\)')
battleye_regexp = re.compile(r'since ([^.]+).')


class ListedWorld(abc.BaseWorld):
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
    battleye_protected: :class:`bool`
        Whether the server is currently protected with BattlEye or not.
    battleye_date: :class:`datetime.date`
        The date when BattlEye was added to this world.
        If this is ``None`` and the world is protected, it means the world was protected from the beginning.
    experimental: :class:`bool`
        Whether the world is experimental or not.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    tournament_world_type: :class:`TournamentWorldType`
        The type of tournament world. ``None`` if this is not a tournament world.
    """
    def __init__(self, name, location=None, pvp_type=None, **kwargs):
        self.name = name  # type: str
        self.location = try_enum(WorldLocation, location)
        self.pvp_type = try_enum(PvpType, pvp_type)
        self.status = kwargs.get("status")  # type: str
        self.online_count = kwargs.get("online_count", 0)  # type: int
        self.transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self.battleye_protected = kwargs.get("battleye_protected", False)  # type: bool
        self.battleye_date = try_date(kwargs.get("battleye_date"))
        self.experimental = kwargs.get("experimental", False)  # type: bool
        self.premium_only = kwargs.get("premium_only", False)  # type: bool
        self.tournament_world_type = try_enum(TournamentWorldType, kwargs.get("tournament_world_type"), None)

    # region Public methods
    @classmethod
    def get_list_url(cls):
        """
        Gets the URL to the World Overview page in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return WorldOverview.get_url()

    @classmethod
    def get_list_url_tibiadata(cls):
        """
        Gets the URL to the World Overview page in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return WorldOverview.get_url_tibiadata()

    @classmethod
    def list_from_content(cls, content):
        """Parses the content of the World Overview section from Tibia.com and returns only the list of worlds.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`list` of :class:`ListedWorld`
            A list of the worlds and their current information.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the worlds section in Tibia.com
        """
        world_overview = WorldOverview.from_content(content)
        return world_overview.worlds

    @classmethod
    def list_from_tibiadata(cls, content):
        """Parses the content of the World Overview section from TibiaData.com.

        Notes
        -----
        Due to TibiaData limitations, the listed worlds lack some information.
        The following attributes are unavailable:

        - :py:attr:`status` is always ``Online``.
        - :py:attr:`battleye_protected` is always ``False``
        - :py:attr:`battleye_date` is always ``None``.

        Parameters
        ----------
        content: :class:`str`
            The JSON response of the worlds section in TibiaData.com

        Returns
        -------
        :class:`list` of :class:`ListedWorld`
            A list of the worlds and their current information.

        Raises
        ------
        InvalidContent
            If the provided content is the json content of the world section in TibiaData.com
        """
        world_overview = WorldOverview.from_tibiadata(content)
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
                self.tournament_world_type = TournamentWorldType.REGUlAR
    # endregion


class World(abc.BaseWorld):
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
    battleye_protected: :class:`bool`
        Whether the server is currently protected with BattlEye or not.
    battleye_date: :class:`datetime.date`
        The date when BattlEye was added to this world.
        If this is ``None`` and the world is protected, it means the world was protected from the beginning.
    experimental: :class:`bool`
        Whether the world is experimental or not.
    tournament_world_type: :class:`TournamentWorldType`
        The type of tournament world. ``None`` if this is not a tournament world.
    online_players: :obj:`list` of :class:`OnlineCharacter`.
        A list of characters currently online in the server.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    """
    __slots__ = (
        "record_count",
        "record_date",
        "creation_date",
        "world_quest_titles",
        "online_players"
    )

    def __init__(self, name, location=None, pvp_type=None, **kwargs):
        self.name = name  # type: str
        self.location = try_enum(WorldLocation, location)
        self.pvp_type = try_enum(PvpType, pvp_type)
        self.status = kwargs.get("status")  # type: bool
        self.online_count = kwargs.get("online_count", 0)  # type: int
        self.record_count = kwargs.get("record_count", 0)  # type: int
        self.record_date = try_datetime(kwargs.get("record_date"))
        self.creation_date = kwargs.get("creation_date")  # type: str
        self.transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self.world_quest_titles = kwargs.get("world_quest_titles", [])  # type: List[str]
        self.battleye_protected = kwargs.get("battleye_protected", False)  # type: bool
        self.battleye_date = try_date(kwargs.get("battleye_date"))
        self.experimental = kwargs.get("experimental", False)  # type: bool
        self.online_players = kwargs.get("online_players", [])  # type: List[OnlineCharacter]
        self.premium_only = kwargs.get("premium_only", False)  # type: bool
        self.tournament_world_type = try_enum(TournamentWorldType, kwargs.get("tournament_world_type"), None)

    # region Properties
    @property
    def creation_year(self):
        """:class:`int`: Returns the year when the world was created."""
        return int(self.creation_date.split("-")[0]) if self.creation_date else None

    @property
    def creation_month(self):
        """:class:`ìnt`: Returns the month when the world was created."""
        return int(self.creation_date.split("-")[1])if self.creation_date else None
    # endregion

    # region Public methods
    @classmethod
    def from_content(cls, content):
        """Parses a Tibia.com response into a :class:`World`.

        Parameters
        ----------
        content: :class:`str`
            The raw HTML from the server's information page.

        Returns
        -------
        :class:`World`
            The World described in the page, or ``None``.

        Raises
        ------
        InvalidContent
            If the provided content is not the html content of the world section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        try:
            error = tables.get("Error")
            if error and error[0].text == "World with this name doesn't exist!":
                return None
            selected_world = parsed_content.find('option', selected=True)
            world = cls(selected_world.text)
            world._parse_world_info(tables.get("World Information", []))

            online_table = tables.get("Players Online", [])
            world.online_players = []
            for row in online_table[1:]:
                cols_raw = row.find_all('td')
                name, level, vocation = (c.text.replace('\xa0', ' ').strip() for c in cols_raw)
                world.online_players.append(OnlineCharacter(name, world.name, int(level), vocation))
        except AttributeError:
            raise InvalidContent("content is not from the world section in Tibia.com")

        return world

    @classmethod
    def from_tibiadata(cls, content):
        """Parses a TibiaData.com response into a :class:`World`

        Parameters
        ----------
        content: :class:`str`
            The raw JSON content from TibiaData

        Returns
        -------
        :class:`World`
            The World described in the page, or ``None``.

        Raises
        ------
        InvalidContent
            If the provided content is not a TibiaData world response.
        """
        json_data = parse_json(content)
        try:
            world_data = json_data["world"]
            world_info = world_data["world_information"]
            world = cls(world_info["name"])
            if "location" not in world_info:
                return None
            world.online_count = world_info["players_online"]
            world.status = "Online" if world.online_count > 0 else "Offline"
            world.record_count = world_info["online_record"]["players"]
            world.record_date = parse_tibiadata_datetime(world_info["online_record"]["date"])
            world.creation_date = world_info["creation_date"]
            world.location = try_enum(WorldLocation, world_info["location"])
            world.pvp_type = try_enum(PvpType, world_info["pvp_type"])
            world.transfer_type = try_enum(TransferType, world_info.get("transfer_type"), TransferType.REGULAR)
            world.premium_only = "premium_type" in world_info
            world.world_quest_titles = world_info.get("world_quest_titles", [])
            world._parse_battleye_status(world_info.get("battleye_status", ""))
            world.experimental = world_info.get("Game World Type:", "Regular") != "Regular"
            for player in world_data.get("players_online", []):
                world.online_players.append(OnlineCharacter(player["name"], world.name, player["level"],
                                                            player["vocation"]))
            return world
        except KeyError:
            raise InvalidContent("content is not a world json response from TibiaData")
    # endregion

    # region Private methods
    def _parse_world_info(self, world_info_table):
        """
        Parses the World Information table from Tibia.com and adds the found values to the object.

        Parameters
        ----------
        world_info_table: :class:`list`[:class:`bs4.Tag`]
        """
        world_info = {}
        for row in world_info_table:
            cols_raw = row.find_all('td')
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
        self.creation_date = "%d-%02d" % (year, month)

        for k, v in world_info.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    def _parse_battleye_status(self, battleye_string):
        """Parses the BattlEye string and applies the results.

        Parameters
        ----------
        battleye_string: :class:`str`
            String containing the world's Battleye Status.
        """
        m = battleye_regexp.search(battleye_string)
        if m:
            self.battleye_protected = True
            self.battleye_date = parse_tibia_full_date(m.group(1))
        else:
            self.battleye_protected = False
            self.battleye_date = None

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parses the information tables found in a world's information page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[:class:`str`, :class:`list`[:class:`bs4.Tag`]]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.find_all('div', attrs={'class': 'TableContainer'})
        output = OrderedDict()
        for table in tables:
            title = table.find("div", attrs={'class': 'Text'}).text
            title = title.split("[")[0].strip()
            inner_table = table.find("div", attrs={'class': 'InnerTableContainer'})
            output[title] = inner_table.find_all("tr")
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
    worlds: :class:`list` of :class:`ListedWorld`
        List of worlds, with limited info.
    """
    __slots__ = ("record_count", "record_date", "worlds")

    def __init__(self, **kwargs):
        self.record_count = kwargs.get("record_count", 0)  # type: int
        self.record_date = try_datetime(kwargs.get("record_date"))
        self.worlds = kwargs.get("worlds", [])  # type: List[ListedWorld]

    def __repr__(self):
        return "<%s total_online=%d>" % (self.__class__.__name__, self.total_online)

    @property
    def total_online(self):
        """:class:`int`: Total players online across all worlds."""
        return sum(w.online_count for w in self.worlds)

    @property
    def tournament_worlds(self):
        """:class:`list` of :class:`GuildMember`: List of tournament worlds.

        Note that tournament worlds are not listed when there are no active or upcoming tournaments."""
        return [w for w in self.worlds if w.tournament_world_type is not None]

    @property
    def regular_worlds(self):
        """:class:`list` of :class:`ListedWorld`: List of worlds that are not tournament worlds."""
        return [w for w in self.worlds if w.tournament_world_type is None]

    @classmethod
    def get_url(cls):
        """
        Gets the URL to the World Overview page in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return get_tibia_url("community", "worlds")

    @classmethod
    def get_url_tibiadata(cls):
        """
        Gets the URL to the World Overview page in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return "https://api.tibiadata.com/v2/worlds.json"

    @classmethod
    def from_content(cls, content):
        """Parses the content of the World Overview section from Tibia.com into an object of this class.

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
        parsed_content = parse_tibiacom_content(content, html_class="TableContentAndRightShadow")
        world_overview = WorldOverview()
        try:
            record_row, *rows = parsed_content.find_all("tr")
            m = record_regexp.search(record_row.text)
            world_overview.record_count = parse_integer(m.group("count"))
            world_overview.record_date = parse_tibia_datetime(m.group("date"))
            world_rows = rows
            world_overview._parse_worlds(world_rows)
            return world_overview
        except (AttributeError, KeyError, ValueError):
            raise InvalidContent("content does not belong to the World Overview section in Tibia.com")

    @classmethod
    def from_tibiadata(cls, content):
        """Parses the content of the World Overview section from TibiaData.com into an object of this class.

        Notes
        -----
        Due to TibiaData limitations, :py:attr:`record_count` and :py:attr:`record_date` are unavailable
        object.

        Additionally, the listed worlds in :py:attr:`worlds` lack some information when obtained from TibiaData.
        The following attributes are unavailable:

        - :py:attr:`ListedWorld.status` is always ``Online``.
        - :py:attr:`ListedWorld.battleye_protected` is always ``False``
        - :py:attr:`ListedWorld.battleye_date` is always ``None``.


        Parameters
        ----------
        content: :class:`str`
            The JSON response of the worlds section in TibiaData.com

        Returns
        -------
        :class:`WorldOverview`
            An instance of this class containing only the available worlds.

        Raises
        ------
        InvalidContent
            If the provided content is the json content of the world section in TibiaData.com
        """
        json_data = parse_json(content)
        try:
            worlds_json = json_data["worlds"]["allworlds"]
            world_overview = cls()
            for world_json in worlds_json:
                world = ListedWorld(world_json["name"], world_json["location"], world_json["worldtype"])
                world._parse_additional_info(world_json["additional"])
                world.online_count = world_json["online"]
                world_overview.worlds.append(world)
            return world_overview
        except KeyError:
            raise InvalidContent("content is not a worlds json response from TibiaData.com.")

    def _parse_worlds(self, world_rows):
        """Parses the world columns and adds the results to :py:attr:`worlds`.

        Parameters
        ----------
        world_rows: :class:`list` of :class:`bs4.Tag`
            A list containing the rows of each world.
        """
        tournament = False
        for world_row in world_rows:
            cols = world_row.find_all("td")
            name = cols[0].text.strip()
            status = "Online"
            if len(cols) == 1 and name == "Tournament Worlds":
                tournament = True
                continue
            elif len(cols) == 1 and name == "Regular Worlds":
                tournament = False
                continue
            elif name == "World":
                continue
            try:
                online = parse_integer(cols[1].text.strip())
            except ValueError:
                online = 0
                status = "Offline"
            location = cols[2].text.replace("\u00a0", " ").strip()
            pvp = cols[3].text.strip()

            world = ListedWorld(name, location, pvp, online_count=online, status=status)
            # Check Battleye icon to get information
            battleye_icon = cols[4].find("span", attrs={"class": "HelperDivIndicator"})
            if battleye_icon is not None:
                world.battleye_protected = True
                m = battleye_regexp.search(battleye_icon["onmouseover"])
                if m:
                    world.battleye_date = parse_tibia_full_date(m.group(1))

            additional_info = cols[5].text.strip()
            world._parse_additional_info(additional_info, tournament)
            self.worlds.append(world)
