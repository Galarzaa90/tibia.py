"""Models related to the highscores section in Tibia.com."""
import datetime
import re
from collections import OrderedDict

from tibiapy.builders.highscores import HighscoresBuilder
from tibiapy.enums import HighscoresCategory, HighscoresProfession, PvpTypeFilter, \
    HighscoresBattlEyeType
from tibiapy.errors import InvalidContent
from tibiapy.models import LoyaltyHighscoresEntry, HighscoresEntry
from tibiapy.utils import parse_form_data, parse_tibiacom_content, try_enum, parse_integer

__all__ = (
    "HighscoresParser",
)

results_pattern = re.compile(r'Results: ([\d,]+)')
numeric_pattern = re.compile(r'(\d+)')


class HighscoresParser:
    """Represents the highscores of a world."""

    _ENTRIES_PER_PAGE = 50

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of a highscores page.

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
            If content is not the HTML of a highscore's page.
        """
        parsed_content = parse_tibiacom_content(content)
        form = parsed_content.find("form")
        tables = cls._parse_tables(parsed_content)
        if form is None or "Highscores" not in tables:
            if "Error" in tables and "The world doesn't exist!" in tables["Error"].text:
                return None
            raise InvalidContent("content does is not from the highscores section of Tibia.com")
        builder = HighscoresBuilder()
        cls._parse_filters_table(builder, form)
        if last_update_container := parsed_content.select_one("span.RightArea"):
            m = numeric_pattern.search(last_update_container.text)
            builder.last_updated(datetime.timedelta(minutes=int(m.group(1))) if m else datetime.timedelta())
        entries_table = tables.get("Highscores")
        cls._parse_entries_table(builder, entries_table)
        return builder.build()


    # region Private methods
    @classmethod
    def _parse_entries_table(cls, builder, table):
        """Parse the table containing the highscore entries.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the entries.
        """
        entries = table.find_all("tr")
        if entries is None:
            return
        _, header, *rows = entries
        info_row = rows.pop()
        pages_div, results_div = info_row.find_all("div")
        page_links = pages_div.find_all("a")
        if listed_pages := [int(p.text) for p in page_links]:
            page = next((x for x in range(1, listed_pages[-1] + 1) if x not in listed_pages), listed_pages[-1] + 1)
            builder.current_page(page)
            builder.total_pages(max(int(page_links[-1].text), page))
        builder.results_count(parse_integer(results_pattern.search(results_div.text).group(1)))
        for row in rows:
            cols_raw = row.find_all('td')
            if "There is currently no data" in cols_raw[0].text:
                break
            if cols_raw[0].text == "Rank":
                continue
            if len(cols_raw) <= 2:
                break
            cls._parse_entry(builder, cols_raw)

    @classmethod
    def _parse_filters_table(cls, builder, form):
        """
        Parse the filters table found in a highscores page.

        Parameters
        ----------
        form: :class:`bs4.Tag`
            The table containing the filters.
        """
        data = parse_form_data(form, include_options=True)
        builder.world(data["world"] if data.get("world") else None)
        builder.battleye_filter(try_enum(HighscoresBattlEyeType, parse_integer(data.get("beprotection"), None)))
        builder.category(try_enum(HighscoresCategory, parse_integer(data.get("category"), None)))
        builder.vocation(try_enum(HighscoresProfession, parse_integer(data.get("profession"), None), HighscoresProfession.ALL))
        checkboxes = form.find_all("input", {"type": "checkbox", "checked": "checked"})
        values = [int(c["value"]) for c in checkboxes]
        builder.pvp_types_filter({try_enum(PvpTypeFilter, v) for v in values})
        builder.available_worlds([v for v in data["__options__"]["world"].values() if v])

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parse the information tables found in a highscores page.

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

    @classmethod
    def _parse_entry(cls, builder, cols):
        """Parse an entry's row and adds the result to py:attr:`entries`.

        Parameters
        ----------
        cols: :class:`bs4.ResultSet`
            The list of columns for that entry.
        """
        rank, name, *values = [c.text.replace('\xa0', ' ').strip() for c in cols]
        rank = int(rank)
        extra = None
        if builder._category == HighscoresCategory.LOYALTY_POINTS:
            extra, vocation, world, level, value = values
        else:
            vocation, world, level, value = values
        value = int(value.replace(',', ''))
        level = int(level)
        if builder._category == HighscoresCategory.LOYALTY_POINTS:
            entry = LoyaltyHighscoresEntry(rank=rank, name=name, vocation=vocation, world=world, level=level,
                                           value=value, title=extra)
        else:
            entry = HighscoresEntry(rank=rank, name=name, vocation=vocation, world=world, level=level, value=value)
        builder.add_entry(entry)
    # endregion

