"""Models related to the leaderboard section in Tibia.com."""
from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING, Optional

from tibiapy import errors
from tibiapy.builders.leaderboard import LeaderboardBuilder
from tibiapy.models.leaderboard import LeaderboardEntry, LeaderboardRotation, Leaderboard
from tibiapy.utils import (parse_pagination, parse_tibia_datetime, parse_tibiacom_content, parse_form_data,
                           parse_integer)

if TYPE_CHECKING:
    from bs4 import Tag

__all__ = (
    "LeaderboardParser",
)

rotation_end_pattern = re.compile(r"ends on ([^)]+)")


class LeaderboardParser:
    """Parser for leaderboards."""

    @classmethod
    def from_content(cls, content: str) -> Optional[Leaderboard]:
        """Parse the content of the leaderboards page.

        Parameters
        ----------
        content:
            The HTML content of the leaderboards page.

        Returns
        -------
            The leaderboard, if found.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.select("table.TableContent")
            form = parsed_content.select_one("form")
            form_data = parse_form_data(form)
            current_world = form_data.values["world"]
            if current_world is None:
                return None

            current_rotation = None
            rotations = []
            for label, value in form_data.available_options["rotation"].items():
                current = False
                if "Current" in label:
                    label = "".join(rotation_end_pattern.findall(label))
                    current = True

                rotation_end = parse_tibia_datetime(label)
                rotation = LeaderboardRotation(rotation_id=int(value), end_date=rotation_end, is_current=current)
                if value == form_data.values["rotation"]:
                    current_rotation = rotation

                rotations.append(rotation)

            builder = (LeaderboardBuilder()
                       .world(current_world)
                       .rotation(current_rotation)
                       .available_worlds([w for w in form_data.available_options["world"].values() if w])
                       .available_rotations(rotations))
            if current_rotation and current_rotation.is_current:
                last_update_table = tables[2]
                if numbers := re.findall(r"(\d+)", last_update_table.text):
                    builder.last_updated(now - datetime.timedelta(minutes=int(numbers[0])))

            cls._parse_entries(builder, tables[-1])
            pagination_block = parsed_content.select_one("small")
            pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
            builder.current_page(pages).total_pages(total).results_count(count)
            return builder.build()
        except (AttributeError, ValueError, KeyError) as e:
            raise errors.InvalidContentError("content does not belong to the leaderboards", e) from e

    @classmethod
    def _parse_entries(cls, builder: LeaderboardBuilder, entries_table: Tag) -> None:
        entries_rows = entries_table.select("tr[style]")
        for row in entries_rows:
            columns = row.select("td")
            if len(columns) != 3:
                continue

            rank = parse_integer(columns[0].text.replace(".", ""))
            points = parse_integer(columns[2].text)
            name_link = columns[1].select_one("a")
            name = name_link.text if name_link else None
            builder.add_entry(LeaderboardEntry(rank=rank, drome_level=points, name=name))
