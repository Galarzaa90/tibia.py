"""Models related to the kill statistics section in Tibia.com."""
from typing import Optional

from tibiapy.builders.kill_statistics import KillStatisticsBuilder
from tibiapy.errors import InvalidContentError
from tibiapy.models import KillStatistics, RaceEntry
from tibiapy.utils import clean_text, get_rows, parse_form_data, parse_tibiacom_content

__all__ = (
    "KillStatisticsParser",
)


class KillStatisticsParser:
    """Parser for kill statistics."""

    @classmethod
    def from_content(cls, content: str) -> Optional[KillStatistics]:
        """Create an instance of the class from the HTML content of the kill statistics' page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The kill statistics contained in the page or None if it doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a kill statistics' page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            entries_table = parsed_content.find("table", attrs={"border": "0", "cellpadding": "3"})
            form = parsed_content.select_one("form")
            form_data = parse_form_data(form)
            builder = (KillStatisticsBuilder()
                       .world(form_data.values["world"])
                       .available_worlds(list(form_data.available_options["world"].values())))
            if not entries_table:
                entries_table = parsed_content.select_one("table.Table3")
            # If the entries table doesn't exist, it means that this belongs to a nonexistent or unselected world.
            if entries_table is None:
                return None

            header, subheader, *rows = get_rows(entries_table)

            for i, row in enumerate(rows):
                columns_raw = row.select("td")
                columns = [clean_text(c) for c in columns_raw]
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
            raise InvalidContentError("content does not belong to a Tibia.com kill statistics page.", e) from e
