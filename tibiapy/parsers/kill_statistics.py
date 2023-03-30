"""Models related to the kill statistics section in Tibia.com."""
from typing import Dict, List

from tibiapy import abc
from tibiapy.builders.kill_statistics import KillStatisticsBuilder
from tibiapy.errors import InvalidContent
from tibiapy.models import KillStatistics, RaceEntry
from tibiapy.utils import get_tibia_url, parse_form_data, parse_tibiacom_content

__all__ = (
    "KillStatisticsParser",
)


class KillStatisticsParser:


    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the HTML content of the kill statistics' page.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`KillStatistics`
            The kill statistics contained in the page or None if it doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a kill statistics' page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            entries_table = parsed_content.find('table', attrs={'border': '0', 'cellpadding': '3'})
            form = parsed_content.select_one("form")
            data = parse_form_data(form, include_options=True)
            builder = KillStatisticsBuilder()\
                .world(data["world"])\
                .available_worlds(list(data["__options__"]["world"].values()))
            if not entries_table:
                entries_table = parsed_content.select_one("table.Table3")
            # If the entries table doesn't exist, it means that this belongs to a nonexistent or unselected world.
            if entries_table is None:
                return None
            header, subheader, *rows = entries_table.select('tr')

            for i, row in enumerate(rows):
                columns_raw = row.select('td')
                columns = [c.text.replace('\xa0', ' ').strip() for c in columns_raw]
                if not columns[2].isnumeric():
                    continue
                entry = RaceEntry(last_day_players_killed=int(columns[1]),
                                  last_day_killed=int(columns[2]),
                                  last_week_players_killed=int(columns[3]),
                                  last_week_killed=int(columns[4]))
                if i == len(rows) - 1:
                    builder.total(entry)
                else:
                    builder.set_entry(columns[0], entry)
            return builder.build()
        except (AttributeError, KeyError) as e:
            raise InvalidContent("content does not belong to a Tibia.com kill statistics page.", e)

