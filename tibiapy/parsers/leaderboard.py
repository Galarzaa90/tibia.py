"""Models related to the leaderboard section in Tibia.com."""
import datetime
import re

from tibiapy import errors
from tibiapy.builders.leaderboard import LeaderboardBuilder
from tibiapy.models.leaderboards import LeaderboardEntry, LeaderboardRotation
from tibiapy.utils import parse_form_data, parse_pagination, parse_tibia_datetime, parse_tibiacom_content

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
            data = parse_form_data(form, include_options=True)
            current_world = data["world"]
            current_rotation = None
            rotations = []
            for label, value in data["__options__"]["rotation"].items():
                current = False
                if "Current" in label:
                    label = "".join(rotation_end_pattern.findall(label))
                    current = True
                rotation_end = parse_tibia_datetime(label)
                rotation = LeaderboardRotation(rotation_id=int(value), end_date=rotation_end, current=current)
                if value == data["rotation"]:
                    current_rotation = rotation
                rotations.append(rotation)
            builder = LeaderboardBuilder()\
                .world(current_world)\
                .rotation(current_rotation)\
                .available_worlds([w for w in data["__options__"]["world"].values() if w])\
                .available_rotations(rotations)
            if current_rotation and current_rotation.current:
                last_update_table = tables[2]
                numbers = re.findall(r'(\d+)', last_update_table.text)
                if numbers:
                    builder.last_update(datetime.timedelta(minutes=int(numbers[0])))
            cls._parse_entries(builder, tables[-1])
            pagination_block = parsed_content.select_one("small")
            pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
            builder.page(pages).total_pages(total).results_count(count)
            return builder.build()
        except (AttributeError, ValueError, KeyError) as e:
            raise errors.InvalidContent("content does not belong to the leaderboards", e)

    @classmethod
    def _parse_entries(cls, builder, entries_table):
        entries_rows = entries_table.select("tr[style]")
        for row in entries_rows:
            columns_raw = row.select("td")
            cols = [c.text for c in columns_raw]
            rank, name, points = cols
            builder.add_entry(LeaderboardEntry(rank=int(rank.replace(".", "")), name=name, drome_level=int(points)))

