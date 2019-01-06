from collections import OrderedDict

from tibiapy import abc, InvalidContent, VocationFilter, Category
from tibiapy.utils import parse_tibiacom_content, try_enum

__all__ = ("Highscores", "HighscoresEntry")


class Highscores(abc.Serializable):
    def __init__(self, world, category, **kwargs):
        self.world = world
        self.category = try_enum(Category, category)
        self.vocation = try_enum(VocationFilter, kwargs.get("vocation"), VocationFilter.ALL)
        self.entries = kwargs.get("entries", [])
        self.results_count = kwargs.get("results_count")

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        filters = tables.get("Highscores Filter")
        if filters is None:
            raise InvalidContent()
        world_filter, vocation_filter, category_filter = filters
        world = world_filter.find("option", {"selected": True})["value"]
        vocation = int(vocation_filter.find("option", {"selected": True})["value"])
        category = category_filter.find("option", {"selected": True})["value"]
        highscores = cls(world, category, vocation=vocation)
        entries = tables.get("Highscores")
        if entries is None:
            return None
        return highscores


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


class HighscoresEntry(abc.BaseCharacter):
    def __init__(self, name, rank, vocation, value, extra=None):
        self.name = name
        self.rank = rank
        self.vocation = vocation
        self.value = value
        self.extra = extra
