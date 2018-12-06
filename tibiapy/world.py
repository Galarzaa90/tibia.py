import re
from collections import OrderedDict

import bs4

from tibiapy import abc
from tibiapy.character import OnlineCharacter
from tibiapy.const import WORLD_URL
from tibiapy.utils import parse_tibia_datetime, parse_tibia_full_date

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
    """
    __slots__ = ("name", "status", "online_count", "record_count", "record_date", "location", "pvp_type",
                 "creation_date", "transfer_type", "world_quest_titles", "battleye_protected", "battleye_date", "type",
                 "players_online")

    def __init__(self, name, **kwargs):
        self.name = name
        self.status = kwargs.get("status")
        self.online_count = kwargs.get("online_count", 0)
        self.record_count = kwargs.get("record_count",0)
        self.record_date = kwargs.get("record_date")
        self.location = kwargs.get("location")
        self.pvp_type = kwargs.get("pvp_type")
        self.creation_date = kwargs.get("creation_date")
        self.transfer_type = kwargs.get("transfer_type", "open")
        self.world_quest_titles = kwargs.get("world_quest_titles", [])
        self.battleye_protected = kwargs.get("battleye_protected", False)
        self.battleye_date = kwargs.get("battleye_date")
        self.type = kwargs.get("type")
        self.players_online = kwargs.get("players_online", [])

    def keys(self):
        return list(self.__slots__)

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError as e:
            raise KeyError(item) from None

    @property
    def url(self):
        """:class:`str`: URL to the world's information page on Tibia.com."""
        return self.get_url(self.name)

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

        online_table = tables.get("Players Online")
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
        self.online_count = world_info.pop("players_online")
        m = record_regexp.match(world_info.pop("online_record"))
        if m:
            self.record_count = int(m.group("count"))
            self.record_date = parse_tibia_datetime(m.group("date"))
        if "world_quest_titles" in world_info:
            self.world_quest_titles = [q.strip() for q in world_info.pop("world_quest_titles").split(",")]
        self.type = world_info.pop("game_world_type")
        m = battleye_regexp.search(world_info.pop("battleye_status"))
        if m:
            self.battleye_protected = True
            self.battleye_date = parse_tibia_full_date(m.group(1))
        else:
            self.battleye_date = False
        for k, v in world_info.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

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