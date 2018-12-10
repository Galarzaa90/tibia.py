import json
import re
from collections import OrderedDict

import bs4

from tibiapy import WORLD_URL_TIBIADATA, abc
from tibiapy.character import OnlineCharacter
from tibiapy.const import WORLD_URL
from tibiapy.utils import parse_tibia_datetime, parse_tibia_full_date, parse_tibiadata_datetime

record_regexp = re.compile(r'(?P<count>\d+) players \(on (?P<date>[^)]+)\)')
battleye_regexp = re.compile(r'since ([^.]+).')



class World(abc.Serializable):
    """Represents a tibia game server.

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
        The date where the online record was achieved.
    location: :class:`str`
        The physical location of the game servers.
    pvp_type: :class:`str`
        The type of PvP in the world.
    creation_date: :class:`str`
        The month and year the world was created. In MM/YY format.
    transfer_type: :class:`str`
        The type of transfer restrictions this world has.
    world_quest_titles: :obj:`list` of :class:`str`
        List of world quest titles the server has achieved.
    battleye_protected: :class:`bool`
        Whether the server is currently protected with battleye or not.
    battleye_date: :class:`datetime.datetime`
        The date where battleye was added to this world.
        If this is ``None`` and the world is proyected, it means the world was protected from the beginning.
    type: :class:`str`
        The world's type.
    players_online: :obj:`list` of :class:`OnlineCharacter`.
        A list of characters currently online in the server.
    premium_only: :class:`bool`
        Whether only premium account players are allowed to play in this server.
    """
    __slots__ = ("name", "status", "online_count", "record_count", "record_date", "location", "pvp_type",
                 "creation_date", "transfer_type", "world_quest_titles", "battleye_protected", "battleye_date", "type",
                 "premium_only", "players_online")

    def __init__(self, name, location=None, pvp_type=None, **kwargs):
        self.name = name
        self.location = location
        self.pvp_type = pvp_type
        self.status = kwargs.get("status")
        self.online_count = kwargs.get("online_count", 0)
        self.record_count = kwargs.get("record_count",0)
        self.record_date = kwargs.get("record_date")
        self.creation_date = kwargs.get("creation_date")
        self.transfer_type = kwargs.get("transfer_type", "open")
        self.world_quest_titles = kwargs.get("world_quest_titles", [])
        self.battleye_protected = kwargs.get("battleye_protected", False)
        self.battleye_date = kwargs.get("battleye_date")
        self.type = kwargs.get("type")
        self.players_online = kwargs.get("players_online", [])
        self.premium_only = kwargs.get("premium_only", False)

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} location={0.location!r} pvp_type={0.pvp_type!r}>".format(self)

    @property
    def url(self):
        """:class:`str`: URL to the world's information page on Tibia.com."""
        return self.get_url(self.name)

    @property
    def url_tibiadata(self):
        """:class:`str`: URL to the world's information page on TibiaData.com."""
        return self.get_url_tibiadata(self.name)

    @classmethod
    def get_url(cls, name):
        """Gets the URL to the World's information page on Tibia.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the world's information page.
        """
        return WORLD_URL % name.title()

    @classmethod
    def get_url_tibiadata(cls, name):
        """Gets the URL to the World's information page on TibiaData.com.

        Parameters
        ----------
        name: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the world's information page on TibiaData.com.
        """
        return WORLD_URL_TIBIADATA % name.title()
    
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
        """
        world = cls._parse(content)
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
        """
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            return None
        try:
            world_data = json_data["world"]
            world_info = world_data["world_information"]
            world = cls(world_info["name"])
            world.online_count = world_info["players_online"]
            world.status = "Online" if world.online_count > 0 else "Offline"
            world.record_count = world_info["online_record"]["players"]
            world.record_date = parse_tibiadata_datetime(world_info["online_record"]["date"])
            try:
                world.creation_date = "%s/%s" % (world_info["creation_date"][-2:], world_info["creation_date"][2:4])
            except IndexError:
                world.creation_date = world_info["creation_date"]
            world.location = world_info["location"]
            world.pvp_type = world_info["pvp_type"]
            world.premium_only = "premium_type" in world_info
            world.world_quest_titles = world_info.get("world_quest_titles", [])
            world._parse_battleye_status(world_info.get("battleye_status", ""))
            world.type = world_info.get("Game World Type:", "Regular")
            for player in world_data.get("players_online", []):
                world.players_online.append(OnlineCharacter(player["name"], world.name, player["level"], player["vocation"]))
            return world
        except KeyError:
            return None

    @classmethod
    def _beautiful_soup(cls, content):
        """
        Parses HTML content into a BeautifulSoup object.
        Parameters
        ----------
        content: :class:`str`
            The HTML content.

        Returns
        -------
        :class:`bs4.BeautifulSoup`: The parsed content.
        """
        return bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), 'lxml',
                                 parse_only=bs4.SoupStrainer("div", class_="BoxContent"))

    @classmethod
    def _parse(cls, content):
        parsed_content = cls._beautiful_soup(content)
        tables = cls._parse_tables(parsed_content)
        if len(tables) == 1:
            return None
        selected_world = parsed_content.find('option', selected=True)
        world = cls(selected_world.text)
        world._parse_world_info(tables.get("World Information", []))

        online_table = tables.get("Players Online", [])
        world.players_online = []
        for row in online_table[1:]:
            cols_raw = row.find_all('td')
            name, level, vocation = (c.text.replace('\xa0', ' ').strip() for c in cols_raw)
            world.players_online.append(OnlineCharacter(name, world.name, int(level), vocation))

        return world

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
            self.online_count = int(world_info.pop("players_online"))
        except KeyError:
            self.online_count = 0
        m = record_regexp.match(world_info.pop("online_record"))
        if m:
            self.record_count = int(m.group("count"))
            self.record_date = parse_tibia_datetime(m.group("date"))
        if "world_quest_titles" in world_info:
            self.world_quest_titles = [q.strip() for q in world_info.pop("world_quest_titles").split(",")]
        self.type = world_info.pop("game_world_type")
        self._parse_battleye_status(world_info.pop("battleye_status"))
        self.premium_only = "premium_type" in world_info
        for k, v in world_info.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    def _parse_battleye_status(self, battleye_string):
        """Parses the battleye string and applies the results.

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

class WorldOverview(abc.Serializable):
    """Container class for the World Overview.

    Attributes
    ----------
    record_count: :class:`int`
        The overall player online record.
    record_date: :class:`datetime.date`
        The date where the record was achieved.
    worlds: :class:`list` of :class:`World`
        List of worlds, with limited info.
    """
    __slots__ = ("record_count", "record_date", "worlds")

    def __init__(self, **kwargs):
        self.record_count = kwargs.get("record_count", 0)
        self.record_date = kwargs.get("record_date", 0)
        self.worlds = kwargs.get("worlds", [])

    def __repr__(self):
        return "<%s total_online=%d>" % (self.__class__.__name__, self.total_online)

    @property
    def total_online(self):
        """:class:`int`: Total players online across all worlds."""
        return sum(w.online_count for w in self.worlds)

    @classmethod
    def get_url(cls):
        """
        Gets the URL to the World Overview page in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the World Overview's page.
        """
        return "https://www.tibia.com/community/?subtopic=worlds"

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

        Notes
        -----
        The :class:`World` elements contained in the attribute ``worlds`` only contain the following attributes:

        - :py:attr:`World.name`
        - :py:attr:`World.online_count`
        - :py:attr:`World.location`
        - :py:attr:`World.status`
        - :py:attr:`World.pvp_type`
        - :py:attr:`World.battleye_protected`
        - :py:attr:`World.battleye_date`
        - :py:attr:`World.premium_only`
        - :py:attr:`World.type`

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`WorldOverview`
            An instance of this class containing all the information.
        """
        parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), 'lxml',
                          parse_only=bs4.SoupStrainer("div", class_="TableContentAndRightShadow"))
        world_overview = cls()
        rows = parsed_content.find_all("tr")
        m = record_regexp.search(rows[0].text)
        if not m:
            return None
        world_overview.record_count = int(m.group("count"))
        world_overview.record_date = parse_tibia_datetime(m.group("date"))
        world_rows = rows[2:]
        world_overview._parse_worlds(world_rows)
        return world_overview

    def _parse_worlds(self, world_rows):
        for world_row in world_rows:
            cols = world_row.find_all("td")
            name = cols[0].text.strip()
            status = "Online"
            try:
                online = int(cols[1].text.strip())
            except ValueError:
                online = 0
                status = "Offline"
            location = cols[2].text.replace("\u00a0", " ").strip()
            pvp = cols[3].text.strip()

            battleye_icon = cols[4].find("span", attrs={"class": "HelperDivIndicator"})
            battleye_protected = False
            battleye_date = None
            if battleye_icon is not None:
                battleye_protected = True
                m = battleye_regexp.search(battleye_icon["onmouseover"])
                if m:
                    battleye_date = parse_tibia_full_date(m.group(1))

            additional_info = cols[5].text.strip()
            premium, transfer_type, world_type = self._parse_additional_info(additional_info)
            self.worlds.append(World(name, location, pvp, online_count=online, transfer_type=transfer_type,
                                     type=world_type, premium_only=premium, battleye_protected=battleye_protected,
                                     battleye_date=battleye_date, status=status))

    @classmethod
    def _parse_additional_info(cls, additional_info):
        if "blocked" in additional_info:
            transfer_type = "blocked"
        elif "locked" in additional_info:
            transfer_type = "locked"
        else:
            transfer_type = "open"
        if "experimental" in additional_info:
            world_type = "Experimental"
        else:
            world_type = "Regular"
        premium = "premium" in additional_info
        return premium, transfer_type, world_type

    @classmethod
    def from_tibiadata(cls, content):
        """Parses the content of the World Overview section from Tibiaata.com into an object of this class.

        Notes
        -----
        Due to TibiaData limitations, the resulting object only contains the :py:attr:`worlds` attribute.
        Also, :class:`World` elements contained in the attribute ``worlds`` only contain the following attributes:

        - :py:attr:`World.name`
        - :py:attr:`World.online_count`
        - :py:attr:`World.location`
        - :py:attr:`World.pvp_type`
        - :py:attr:`World.premium_only`
        - :py:attr:`World.type`

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`WorldOverview`
            An instance of this class containing all the information.
        """
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            return None
        try:
            worlds = json_data["worlds"]["allworlds"]
            world_overview = cls()
            for world in worlds:
                premium, transfer_type, world_type = cls._parse_additional_info(world["additional"])
                world_overview.worlds.append(World(world["name"], world["location"], world["worldtype"],
                                                   online_count=world["online"], premium_only=premium,
                                                   transfer_type=transfer_type, type=world_type))
            return world_overview
        except KeyError:
            return None


