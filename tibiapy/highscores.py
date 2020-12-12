import datetime
import re
from collections import OrderedDict
from typing import List, Optional

from tibiapy import abc
from tibiapy.enums import Category, Vocation, VocationFilter, BattlEyeTypeFilter, PvpTypeFilter, \
    BattlEyeHighscoresFilter
from tibiapy.errors import InvalidContent
from tibiapy.utils import get_tibia_url, parse_tibiacom_content, try_enum, parse_integer

__all__ = (
    "Highscores",
    "HighscoresEntry",
    "LoyaltyHighscoresEntry",
)

results_pattern = re.compile(r'Results: ([\d,]+)')
numeric_pattern = re.compile(r'(\d+)')


class Highscores(abc.Serializable):
    """Represents the highscores of a world.

    .. versionadded:: 1.1.0

    Attributes
    ----------
    world: :class:`str`
        The world the highscores belong to. If this is :obj:`None`, the highscores shown are for all worlds.
    category: :class:`Category`
        The selected category to displays the highscores of.
    vocation: :class:`VocationFilter`
        The selected vocation to filter out values.
    battleye_filter: :class:`BattlEyeHighscoresFilter`
        The selected BattlEye filter. If :obj:`None`, all worlds will be displayed.

        Only applies for global highscores. Only characters from worlds with the matching BattlEye protection will be
        shown.
    pvp_types_filter: :class:`list` of :class:`PvpTypeFilter`
        The selected PvP types filter. If :obj:`None`, all world will be displayed.

        Only applies for global highscores. Only characters from worlds with the matching PvP type will be shown.
    page: :class:`int`
        The page number being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results_count: :class:`int`
        The total amount of highscores entries in this category. These may be shown in another page.
    last_updated: :class:`datetime.timedelta`
        How long ago were this results updated. The resolution is 1 minute.
    entries: :class:`list` of :class:`HighscoresEntry`
        The highscores entries found.
    """
    _ENTRIES_PER_PAGE = 50

    def __init__(self, world, category=Category.EXPERIENCE, **kwargs):
        self.world: Optional[str] = world
        self.category: Category = try_enum(Category, category, Category.EXPERIENCE)
        self.vocation: VocationFilter = try_enum(VocationFilter, kwargs.get("vocation"), VocationFilter.ALL)
        self.battleye_filter: Optional[BattlEyeTypeFilter] = try_enum(BattlEyeTypeFilter, kwargs.get("battleye_filter"))
        self.pvp_types_filter: List[PvpTypeFilter] = kwargs.get("pvp_types_filter", [])
        self.entries: List[HighscoresEntry] = kwargs.get("entries", [])
        self.results_count: int = kwargs.get("results_count", 0)
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)

    __slots__ = (
        'world',
        'category',
        'vocation',
        'battleye_filter',
        "pvp_types_filter",
        'page',
        'total_pages',
        'results_count',
        'last_updated',
        'entries',
    )

    _serializable_properties = (

    )

    def __repr__(self):
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
    def url(self):
        """:class:`str`: The URL to the highscores page on Tibia.com containing the results."""
        return self.get_url(self.world, self.category, self.vocation, self.page, self.battleye_filter,
                            self.pvp_types_filter)

    @property
    def previous_page_url(self):
        """:class:`str`: The URL to the previous page of the current highscores, if there's any."""
        return self.get_page_url(self.page - 1) if self.page > 1 else None

    @property
    def next_page_url(self):
        """:class:`str`: The URL to the next page of the current highscores, if there's any."""
        return self.get_page_url(self.page + 1) if self.page < self.total_pages else None

    def get_page_url(self, page):
        """Gets the URL to a specific page for the current highscores.

        Parameters
        ----------
        page: :class:`int`
            The page to get the URL for.

        Returns
        -------
        :class:`str`
            The URL to the page of the current highscores.

        Raises
        ------
        ValueError
            The provided page is less or equals than zero.
        """
        if page <= 0:
            raise ValueError("page cannot be less or equals than zero")
        return self.get_url(self.world, self.category, self.vocation, page, self.battleye_filter, self.pvp_types_filter)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of a highscores page.

        Notes
        -----
        Tibia.com only shows up to 50 entries per page, so in order to obtain the full highscores, all pages must be
        obtained individually and merged into one.

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
            if "Error" in tables and "The world doesn't exist!" in tables["Error"].text:
                return None
            raise InvalidContent("content does is not from the highscores section of Tibia.com")
        highscores = cls(None)
        highscores._parse_filters_table(filters)
        last_update_container = parsed_content.find("span", attrs={"class": "RightArea"})
        if last_update_container:
            m = numeric_pattern.search(last_update_container.text)
            highscores.last_updated = datetime.timedelta(minutes=int(m.group(1))) if m else datetime.timedelta()
        entries_table = tables.get("Highscores")
        highscores._parse_entries_table(entries_table)
        return highscores

    @classmethod
    def get_url(cls, world=None, category=Category.EXPERIENCE, vocation=VocationFilter.ALL, page=1,
                battleye_type=None, pvp_types=None):
        """Gets the Tibia.com URL of the highscores for the given parameters.

        Parameters
        ----------
        world: :class:`str`, optional
            The game world of the desired highscores. If no world is passed, ALL worlds are shown.
        category: :class:`Category`
            The desired highscores category.
        vocation: :class:`VocationFilter`
            The vocation filter to apply. By default all vocations will be shown.
        page: :class:`int`
            The page of highscores to show.
        battleye_type: :class:`BattlEyeHighscoresFilter`, optional
            The battleEye filters to use.
        pvp_types: :class:`list` of :class:`PvpTypeFilter`, optional
            The list of PvP types to filter the results for.
        Returns
        -------
        The URL to the Tibia.com highscores.
        """
        pvp_types = pvp_types or []
        pvp_params = [("worldtypes[]", p.value) for p in pvp_types]
        return get_tibia_url("community", "highscores", *pvp_params, world=world, category=category.value,
                             profession=vocation.value, currentpage=page,
                             beprotection=battleye_type.value if battleye_type else None)

    # region Private methods
    def _parse_entries_table(self, table):
        """Parses the table containing the highscore entries

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the entries.
        """
        entries = table.find_all("tr")
        if entries is None:
            return None
        _, header, *rows = entries
        info_row = rows.pop()
        pages_div, results_div = info_row.find_all("div")
        page_links = pages_div.find_all("a")
        listed_pages = [int(p.text) for p in page_links]
        if listed_pages:
            self.page = next((x for x in range(1, listed_pages[-1] + 1) if x not in listed_pages), 0)
            self.total_pages = max(int(page_links[-1].text), self.page)
        self.results_count = parse_integer(results_pattern.search(results_div.text).group(1))
        for row in rows:
            cols_raw = row.find_all('td')
            if "There is currently no data" in cols_raw[0].text:
                break
            self._parse_entry(cols_raw)

    def _parse_filters_table(self, table):
        """
        Parses the filters table found in a highscores page.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the filters.
        """
        dropdowns = {s["name"]: s for s in table.find_all("select")}
        selected_world = dropdowns["world"].find("option", {"selected": "selected"})
        if selected_world:
            value = selected_world["value"]
            self.world = value if value and "All Worlds" not in value else None
        selected_be = dropdowns["beprotection"].find("option", {"selected": "selected"})
        if selected_be:
            value = selected_be["value"]
            num_value = int(value)
            self.battleye_filter = try_enum(BattlEyeHighscoresFilter, num_value)
        selected_profession = dropdowns["profession"].find("option", {"selected": "selected"})
        if selected_profession:
            value = selected_profession["value"]
            num_value = int(value)
            self.vocation = try_enum(VocationFilter, num_value, VocationFilter.ALL)
        selected_category = dropdowns["category"].find("option", {"selected": "selected"})
        if selected_category:
            value = selected_category["value"]
            num_value = int(value)
            self.category = try_enum(Category, num_value)
        checkboxes = table.find_all("input", {"type": "checkbox", "checked": "checked"})
        values = [int(c["value"]) for c in checkboxes]
        self.pvp_types_filter = [try_enum(PvpTypeFilter, v) for v in values]

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
        :class:`OrderedDict`[:class:`str`, :class:`bs4.Tag`]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.find_all('div', attrs={'class': 'TableContainer'})
        output = OrderedDict()
        for table in tables:
            title = table.find("div", attrs={'class': 'Text'}).text
            title = title.split("[")[0].strip()
            title = re.sub(r'Last Update.*', '', title)
            inner_table = table.find("div", attrs={'class': 'InnerTableContainer'})
            output[title] = inner_table
        return output

    def _parse_entry(self, cols):
        """Parses an entry's row and adds the result to py:attr:`entries`.

        Parameters
        ----------
        cols: :class:`bs4.ResultSet`
            The list of columns for that entry.
        """
        rank, name, *values = [c.text.replace('\xa0', ' ').strip() for c in cols]
        rank = int(rank)
        extra = None
        if self.category == Category.LOYALTY_POINTS:
            extra, vocation, world, level, value = values
        else:
            vocation, world, level, value = values
        value = int(value.replace(',', ''))
        level = int(level)
        if self.category == Category.LOYALTY_POINTS:
            entry = LoyaltyHighscoresEntry(rank, name, vocation, world, level, value, extra)
        else:
            entry = HighscoresEntry(rank, name, vocation, world, level, value)
        self.entries.append(entry)
    # endregion


class HighscoresEntry(abc.BaseCharacter, abc.Serializable):
    """Represents a entry for the highscores.

    Attributes
    ----------
    name: :class:`str`
        The name of the character.
    rank: :class:`int`
        The character's rank in the respective highscores.
    vocation: :class:`Vocation`
        The character's vocation.
    world: :class:`str`
        The character's world.
    level: :class:`int`
        The character's level.
    value: :class:`int`
        The character's value for the highscores.
    """
    def __init__(self, rank, name, vocation, world, level, value):
        self.name: str = name
        self.rank: int = rank
        self.vocation = try_enum(Vocation, vocation)
        self.value: int = value
        self.world: str = world
        self.level: int = level

    __slots__ = (
        'rank',
        'name',
        'vocation',
        'world',
        'level',
        'value',
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} rank={self.rank} name={self.name!r} value={self.value}>"


class LoyaltyHighscoresEntry(HighscoresEntry):
    """Represents a entry for the highscores loyalty points category.

    This is a subclass of :class:`HighscoresEntry`, adding an extra field for title.

    Attributes
    ----------
    name: :class:`str`
        The name of the character.
    rank: :class:`int`
        The character's rank in the respective highscores.
    vocation: :class:`Vocation`
        The character's vocation.
    world: :class:`str`
        The character's world.
    level: :class:`int`
        The character's level.
    value: :class:`int`
        The character's loyalty points.
    title: :class:`str`
        The character's loyalty title.
    """
    def __init__(self, rank, name, vocation, world, level, value, title):
        super().__init__(rank, name, vocation, world, level, value)
        self.title: str = title

    __slots__ = (
        'title',
    )
