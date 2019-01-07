import re
from collections import OrderedDict
from typing import List

from tibiapy import Category, InvalidContent, Vocation, VocationFilter, abc
from tibiapy.utils import parse_tibiacom_content, try_enum

__all__ = ("ExpHighscoresEntry", "Highscores", "HighscoresEntry", "LoyaltyHighscoresEntry")

results_pattern = re.compile(r'Results: (\d+)')

HIGHSCORES_URL = "https://secure.tibia.com/community/?subtopic=highscores&world=%s&list=%s&profession=%d&currentpage=%d"

class Highscores(abc.Serializable):
    """Represents the highscores of a world.

    Tibia.com only shows 25 entries per page.
    TibiaData.com shows all results at once.

    Attributes
    ----------
    world: :class:`world`
        The world the highscores belong to.
    category: :class:`Category`
        The selected category to displays the highscores of.
    vocation: :class:`VocationFilter`
        The selected vocation to filter out values.
    results_count: :class:`int`
        The total amount of highscores entries in this category. These may be shown in another page.
    """
    def __init__(self, world, category, **kwargs):
        self.world = world  # type: str
        self.category = try_enum(Category, category, Category.EXPERIENCE)
        self.vocation = try_enum(VocationFilter, kwargs.get("vocation"), VocationFilter.ALL)
        self.entries = kwargs.get("entries", [])  # type: List[HighscoresEntry]
        self.results_count = kwargs.get("results_count")  # type: int

    def __repr__(self) -> str:
        return "<{0.__class__.__name__} world={0.world!r} category={0.category!r} vocation={0.vocation!r}>".format(self)

    @property
    def from_rank(self):
        """:class:`int`: The starting rank of the provided entries."""
        return self.entries[0].rank if self.entries else 0

    @property
    def to_rank(self):
        """:class:`int`: The last rank of the provided entries."""
        return self.entries[-1].rank if self.entries else 0

    @property
    def page(self):
        """:class:`int`: The page number the shown results correspond to on Tibia.com"""
        return int(self.from_rank/25)+1 if self.from_rank else 0

    @property
    def total_pages(self):
        """:class:`int`: The total of pages of the highscores category."""
        return int(self.results_count/25)

    @property
    def url(self):
        """:class:`str`: The URL to the highscores page on Tibia.com containing the results."""
        return self.get_url(self.world, self.category, self.vocation, self.page)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of a highscores page.

        Notes
        -----
        Tibia.com only shows up to 25 entries per page, so in order to obtain the full highscores, all 12 pages must
        be parsed and merged into one.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`Highscores`
            The highscores results contained in the page.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a highscore's page."""
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        filters = tables.get("Highscores Filter")
        if filters is None:
            raise InvalidContent()
        world_filter, vocation_filter, category_filter = filters
        world = world_filter.find("option", {"selected": True})["value"]
        if world == "":
            return None
        category = category_filter.find("option", {"selected": True})["value"]
        vocation_selected = vocation_filter.find("option", {"selected": True})
        vocation = int(vocation_selected["value"]) if vocation_selected else 0
        highscores = cls(world, category, vocation=vocation)
        entries = tables.get("Highscores")
        if entries is None:
            return None
        _, header, *rows = entries
        info_row = rows.pop()
        highscores.results_count = int(results_pattern.search(info_row.text).group(1))
        for row in rows:
            cols_raw = row.find_all('td')
            highscores._parse_entry(cols_raw)
        return highscores

    @classmethod
    def get_url(cls, world, category=Category.EXPERIENCE, vocation=VocationFilter.ALL, page=1):
        """Gets the Tibia.com URL of the highscores for the given parameters.

        Parameters
        ----------
        world: :class:`str`
            The game world of the desired highscores.
        category: :class:`Category`
            The desired highscores category.
        vocation: :class:`VocationFiler`
            The vocation filter to apply. By default all vocations will be shown.
        page: :class:`int`
            The page of highscores to show.

        Returns
        -------
        The URL to the Tibia.com highscores.
        """
        return HIGHSCORES_URL % (world, category.value, vocation.value, page)

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parses the information tables found in a highscores page.

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

    def _parse_entry(self, cols):
        """Parses an entry's row and adds the result to py:attr:`entries`.

        Parameters
        ----------
        cols: :class:`bs4.ResultSet`
            The list of columns for that entry.
        """
        rank, name, vocation, *values = [c.text.replace('\xa0', ' ').strip() for c in cols]
        rank = int(rank)
        if self.category == Category.EXPERIENCE or self.category == Category.LOYALTY_POINTS:
            extra, value = values
        else:
            value, *extra = values
        value = int(value.replace(',', ''))
        if self.category == Category.EXPERIENCE:
            entry = ExpHighscoresEntry(name, rank, vocation, value, int(extra))
        elif self.category == Category.LOYALTY_POINTS:
            entry = LoyaltyHighscoresEntry(name, rank, vocation, value, extra)
        else:
            entry = HighscoresEntry(name, rank, vocation, value)
        self.entries.append(entry)


class HighscoresEntry(abc.BaseCharacter):
    """Represents a entry for the highscores.

    Attributes
    ----------
    name: :class:`str`
        The name of the character.
    rank: :class:`int`
        The character's rank in the respective highscores.
    vocation: :class:`Vocation`
        The character's vocation.
    value: :class:`int`
        The character's value for the highscores."""
    def __init__(self, name, rank, vocation, value):
        self.name = name
        self.rank = rank
        self.vocation = try_enum(Vocation, vocation)
        self.value = value

    def __repr__(self) -> str:
        return "<{0.__class__.__name__} rank={0.rank} name={0.name!r} value={0.value}>".format(self)


class ExpHighscoresEntry(HighscoresEntry):
    """Represents a entry for the highscores's experience category.

        Attributes
        ----------
        name: :class:`str`
            The name of the character.
        rank: :class:`int`
            The character's rank in the respective highscores.
        vocation: :class:`Vocation`
            The character's vocation.
        value: :class:`int`
            The character's experience points.
        level: :class:`int`
            The character's level."""
    def __init__(self, name, rank, vocation, value, level):
        super().__init__(name, rank, vocation, value)
        self.level = level


class LoyaltyHighscoresEntry(HighscoresEntry):
    """Represents a entry for the highscores loyalty points category.

        Attributes
        ----------
        name: :class:`str`
            The name of the character.
        rank: :class:`int`
            The character's rank in the respective highscores.
        vocation: :class:`Vocation`
            The character's vocation.
        value: :class:`int`
            The character's loyalty points.
        title: :class:`str`
            The character's loyalty title."""
    def __init__(self, name, rank, vocation, value, title):
        super().__init__(name, rank, vocation, value)
        self.title = title
