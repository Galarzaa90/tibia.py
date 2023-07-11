"""Models related to the leaderboard section in Tibia.com."""
from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING

from tibiapy import errors
from tibiapy.builders.leaderboard import LeaderboardBuilder
from tibiapy.models.leaderboard import LeaderboardEntry, LeaderboardRotation, Leaderboard
from tibiapy.utils import parse_pagination, parse_tibia_datetime, parse_tibiacom_content, \
    parse_form_data_new

if TYPE_CHECKING:
    from bs4 import Tag

__all__ = (
    'LeaderboardParser',
)

rotation_end_pattern = re.compile(r"ends on ([^)]+)")


class LeaderboardParser:

    @classmethod
    def from_content(cls, content):
        """Parse the content of the leaderboards page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the leaderboards page.

        Returns
        -------
        :class:`Leaderboard`
            The ledaerboard if found.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.select("table.TableContent")
            form = parsed_content.select_one("form")
            form_data = parse_form_data_new(form)
            current_world = form_data.values["world"]
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
            builder = LeaderboardBuilder() \
                .world(current_world) \
                .rotation(current_rotation) \
                .available_worlds([w for w in form_data.available_options["world"].values() if w]) \
                .available_rotations(rotations)
            if current_rotation and current_rotation.is_current:
                last_update_table = tables[2]
                if numbers := re.findall(r'(\d+)', last_update_table.text):
                    builder.last_update(datetime.timedelta(minutes=int(numbers[0])))
            cls._parse_entries(builder, tables[-1])
            pagination_block = parsed_content.select_one("small")
            pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
            builder.current_page(pages).total_pages(total).results_count(count)
            return builder.build()
        except (AttributeError, ValueError, KeyError) as e:
            raise errors.InvalidContent("content does not belong to the leaderboards", e) from e

    @classmethod
    def _parse_entries(cls, builder: LeaderboardBuilder, entries_table: Tag):
        entries_rows = entries_table.select("tr[style]")
        for row in entries_rows:
            columns_raw = row.select("td")
            cols = [c.text for c in columns_raw]
            rank, name, points = cols
            builder.add_entry(LeaderboardEntry(rank=int(rank.replace(".", "")), name=name, drome_level=int(points)))
