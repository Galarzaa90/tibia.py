import re
from collections import OrderedDict

import bs4

from tibiapy.character import OnlineCharacter
from tibiapy.const import WORLD_URL
from tibiapy.utils import parse_tibia_datetime, parse_tibia_full_date

record_regexp = re.compile(r'(?P<count>\d+) players \(on (?P<date>[^)]+)\)')
battleye_regexp = re.compile(r'since ([^.]+).')

class World:
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

    @classmethod
    def get_url(cls, name):
        return WORLD_URL % name.title()
    
    @classmethod
    def from_content(cls, content):
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
        output, tables = cls._parse_tables(parsed_content)
        if len(tables) == 1:
            return None
        selected_world = parsed_content.find('option', selected=True)
        world = cls(selected_world.text)
        world_info = {}
        for row in output.get("World Information", []):
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            world_info[field] = value
        world.online_count = world_info.pop("players_online")
        m = record_regexp.match(world_info.pop("online_record"))
        if m:
            world.record_count= int(m.group("count"))
            world.record_date = parse_tibia_datetime(m.group("date"))
        if "world_quest_titles" in world_info:
            world.world_quest_titles = [q.strip() for q in world_info.pop("world_quest_titles").split(",")]
        world.type = world_info.pop("game_world_type")
        m = battleye_regexp.search(world_info.pop("battleye_status"))
        if m:
            world.battleye_protected = True
            world.battleye_date = parse_tibia_full_date(m.group(1))
        else:
            world.battleye_date = False
        for k,v in world_info.items():
            try:
                setattr(world, k, v)
            except AttributeError:
                pass
        online_table = output.get("Players Online")
        world.players_online = []
        for row in online_table[1:]:
            cols_raw = row.find_all('td')
            name, level, vocation = (c.text.replace('\xa0', ' ').strip() for c in cols_raw)
            world.players_online.append(OnlineCharacter(name, world.name, int(level), vocation))
        return world

    @classmethod
    def _parse_tables(cls, parsed_content):
        tables = parsed_content.find_all('div', attrs={'class': 'TableContainer'})
        output = OrderedDict()
        for table in tables:
            title = table.find("div", attrs={'class': 'Text'}).text
            title = title.split("[")[0].strip()
            inner_table = table.find("div", attrs={'class': 'InnerTableContainer'})
            output[title] = inner_table.find_all("tr")
        return output, tables