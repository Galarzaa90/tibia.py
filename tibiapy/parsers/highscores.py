"""Models related to the highscores section in Tibia.com."""
from __future__ import annotations

import datetime
import re
from collections import OrderedDict
from typing import Dict, Optional, TYPE_CHECKING

import bs4

from tibiapy.builders.highscores import HighscoresBuilder
from tibiapy.enums import HighscoresBattlEyeType, HighscoresCategory, HighscoresProfession, PvpTypeFilter
from tibiapy.errors import InvalidContentError
from tibiapy.models import HighscoresEntry, LoyaltyHighscoresEntry
from tibiapy.utils import clean_text, parse_form_data, parse_integer, parse_pagination, parse_tibiacom_content, try_enum

if TYPE_CHECKING:
    from tibiapy.models import Highscores

__all__ = (
    "HighscoresParser",
)

results_pattern = re.compile(r"Results: ([\d,]+)")
numeric_pattern = re.compile(r"(\d+)")


class HighscoresParser:
    """Represents the highscores of a world."""

    _ENTRIES_PER_PAGE = 50

    @classmethod
    def from_content(cls, content: str) -> Optional[Highscores]:
        """Create an instance of the class from the html content of a highscores page.

        Notes
        -----
        Tibia.com only shows up to 50 entries per page, so to obtain the full highscores, all pages must be
        obtained individually and merged into one.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The highscores results contained in the page.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a highscore's page.
        """
        parsed_content = parse_tibiacom_content(content)
        form = parsed_content.select_one("form")
        tables = cls._parse_tables(parsed_content)
        if form is None or "Highscores" not in tables:
            if "Error" in tables and "The world doesn't exist!" in tables["Error"].text:
                return None

            raise InvalidContentError("content does is not from the highscores section of Tibia.com")

        builder = HighscoresBuilder()
        cls._parse_filters_table(builder, form)
        if last_update_container := parsed_content.select_one("span.RightArea"):
            m = numeric_pattern.search(last_update_container.text)
            last_update = datetime.timedelta(minutes=int(m.group(1))) if m else datetime.timedelta()
            builder.last_updated(datetime.datetime.now(tz=datetime.timezone.utc) - last_update)

        entries_table = tables.get("Highscores")
        cls._parse_entries_table(builder, entries_table)
        return builder.build()

    # region Private methods
    @classmethod
    def _parse_entries_table(cls, builder: HighscoresBuilder, table: bs4.Tag) -> None:
        """Parse the table containing the highscore entries.

        Parameters
        ----------
        builder: :class:`HighscoresBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the entries.
        """
        page, total_pages, results_count = parse_pagination(table.select_one(".PageNavigation"))
        builder.current_page(page).total_pages(total_pages).results_count(results_count)
        rows = table.select("tr[style]")
        for row in rows:
            cols_raw = row.select("td")
            if "There is currently no data" in cols_raw[0].text:
                break

            if cols_raw[0].text == "Rank":
                continue

            if len(cols_raw) <= 2:
                break

            cls._parse_entry(builder, cols_raw)

    @classmethod
    def _parse_filters_table(cls, builder: HighscoresBuilder, form: bs4.Tag) -> None:
        """Parse the filters table found in a highscores page.

        Parameters
        ----------
        builder: :class:`HighscoresBuilder`
            The builder where data will be stored to.
        form: :class:`bs4.Tag`
            The table containing the filters.
        """
        data = parse_form_data(form)
        builder.world(data.values["world"] if data.values.get("world") else None)
        builder.battleye_filter(try_enum(HighscoresBattlEyeType, parse_integer(data.values.get("beprotection"), None)))
        builder.category(try_enum(HighscoresCategory, parse_integer(data.values.get("category"), None)))
        builder.vocation(try_enum(HighscoresProfession, parse_integer(data.values.get("profession"), None),
                                  HighscoresProfession.ALL))
        builder.pvp_types_filter({try_enum(PvpTypeFilter, int(v)) for v in data.values_multiple["worldtypes[]"]})
        builder.available_worlds([v for v in data.available_options["world"].values() if v])

    @classmethod
    def _parse_tables(cls, parsed_content: bs4.BeautifulSoup) -> Dict[str, bs4.Tag]:
        """Parse the information tables found in a highscores page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[:class:`str`, :class:`bs4.Tag`]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.select("div.TableContainer")
        output = OrderedDict()
        for table in tables:
            title = table.select_one("div.Text").text
            title = title.split("[")[0].strip()
            title = re.sub(r"Last Update.*", "", title)
            inner_table = table.select_one("div.InnerTableContainer")
            output[title] = inner_table

        return output

    @classmethod
    def _parse_entry(cls, builder: HighscoresBuilder, cols: bs4.ResultSet) -> None:
        """Parse an entry's row and adds the result to py:attr:`entries`.

        Parameters
        ----------
        builder: :class:`HighscoresBuilder`
            The builder where data will be stored to.
        cols: :class:`bs4.ResultSet`
            The list of columns for that entry.
        """
        rank, name, *values = (clean_text(c) for c in cols)
        rank = int(rank)
        extra = None
        if builder._category == HighscoresCategory.LOYALTY_POINTS:
            extra, vocation, world, level, value = values
        else:
            vocation, world, level, value = values

        value = int(value.replace(",", ""))
        level = int(level)
        if builder._category == HighscoresCategory.LOYALTY_POINTS:
            entry = LoyaltyHighscoresEntry(rank=rank, name=name, vocation=vocation, world=world, level=level,
                                           value=value, title=extra)
        else:
            entry = HighscoresEntry(rank=rank, name=name, vocation=vocation, world=world, level=level, value=value)

        builder.add_entry(entry)
    # endregion
