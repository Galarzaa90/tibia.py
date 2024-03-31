"""Parser for the worlds sections."""
from __future__ import annotations

import datetime
import re
from typing import TYPE_CHECKING, Optional, List

from tibiapy.builders.world import (WorldBuilder, WorldEntryBuilder,
                                    WorldOverviewBuilder)
from tibiapy.enums import (BattlEyeType, PvpType,
                           TransferType, WorldLocation)
from tibiapy.errors import InvalidContentError
from tibiapy.models import OnlineCharacter, WorldEntry
from tibiapy.utils import (parse_integer, parse_tibia_datetime,
                           parse_tibia_full_date, parse_tibiacom_content,
                           try_enum, parse_tables_map, get_rows, clean_text)

if TYPE_CHECKING:
    import bs4
    from tibiapy.models import World, WorldOverview

__all__ = (
    "WorldParser",
    "WorldOverviewParser",
)

record_regexp = re.compile(r"(?P<count>[\d.,]+) players \(on (?P<date>[^)]+)\)")
battleye_regexp = re.compile(r"since ([^.]+).")


class WorldParser:
    """Parses Tibia.com content into worlds."""

    @classmethod
    def from_content(cls, content: str) -> Optional[World]:
        """Parse a Tibia.com response into a :class:`World`.

        Parameters
        ----------
        content:
            The raw HTML from the server's information page.

        Returns
        -------
            The World described in the page, or :obj:`None`.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the world section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parse_tables_map(parsed_content, "div.InnerTableContainer")
        try:
            if tables.get("Error"):
                return None

            selected_world = parsed_content.select_one("option:checked")
            builder = WorldBuilder().name(selected_world.text)
            cls._parse_world_info(builder, tables.get("World Information", []))

            online_table = next((v for k, v in tables.items() if "Players Online" in k), None)
            if not online_table:
                return builder.build()

            for row in online_table.select("tr.Odd, tr.Even"):
                cols_raw = row.select("td")
                name, level, vocation = (clean_text(c) for c in cols_raw)
                builder.add_online_player(OnlineCharacter(name=name, level=int(level), vocation=vocation))

        except AttributeError as e:
            raise InvalidContentError("content is not from the world section in Tibia.com") from e

        return builder.build()

    @classmethod
    def _parse_world_info(cls, builder: WorldBuilder, world_info_table: bs4.Tag) -> None:
        """Parse the World Information table from Tibia.com and adds the found values to the object.

        Parameters
        ----------
        builder: :class:`WorldBuilder`
            The instance of the builder where data will be collected.
        world_info_table: :class:`bs4.Tag`
            The table containing the world's information.
        """
        field_actions = {
            "Status": lambda v: builder.is_online("online" in v.lower()),
            "Players Online": lambda v: builder.online_count(parse_integer(v)),
            "Online Record": lambda v: cls._parse_online_record(builder, v),
            "Creation Date": lambda v: cls._parse_creation_date(builder, v),
            "Location": lambda v: builder.location(try_enum(WorldLocation, v)),
            "PvP Type": lambda v: builder.pvp_type(try_enum(PvpType, v)),
            "Premium Type": lambda v: builder.is_premium_only(True),
            "Transfer Type": lambda v: builder.transfer_type(try_enum(TransferType, v, TransferType.REGULAR)),
            "World Quest Titles": lambda v: cls._parse_world_quest_titles(builder, v),
            "BattlEye Status": lambda v: cls._parse_battleye_status(builder, v),
            "Game World Type": lambda v: builder.is_experimental(v.lower() == "experimental"),
        }
        for row in get_rows(world_info_table):
            cols_raw = row.select("td")
            cols = [clean_text(ele) for ele in cols_raw]
            field, value = cols
            field = field.replace(":", "")
            if field in field_actions:
                action = field_actions[field]
                action(value)

    @classmethod
    def _parse_world_quest_titles(cls, builder: WorldBuilder, value: str) -> None:
        titles = [q.strip() for q in value.split(",")]
        if "currently has no title" not in titles[0]:
            builder.world_quest_titles(titles)

    @classmethod
    def _parse_online_record(cls, builder: WorldBuilder, value: str) -> None:
        if m := record_regexp.match(value):
            builder.record_count(parse_integer(m.group("count")))
            builder.record_date(parse_tibia_datetime(m.group("date")))

    @classmethod
    def _parse_creation_date(cls, builder: WorldBuilder, value: str) -> None:
        parsed_date = datetime.datetime.strptime(value, "%B %Y")
        year, month = parsed_date.year, parsed_date.month
        builder.creation_date(f"{year:d}-{month:02d}")

    @classmethod
    def _parse_battleye_status(cls, builder: WorldBuilder, battleye_string: str) -> None:
        """Parse the BattlEye string and applies the results.

        Parameters
        ----------
        builder: :class:`WorldBuilder`
            The builder instance used to set the values.
        battleye_string: :class:`str`
            String containing the world's BattlEye Status.
        """
        if m := battleye_regexp.search(battleye_string):
            battleye_date = parse_tibia_full_date(m.group(1))
            (builder.battleye_since(battleye_date)
             .battleye_type(BattlEyeType.PROTECTED if battleye_date else BattlEyeType.INITIALLY_PROTECTED)
             )
        else:
            builder.battleye_since(None).battleye_type(BattlEyeType.UNPROTECTED)


class WorldOverviewParser:
    """Parses Tibia.com content from the World Overview section."""

    @classmethod
    def from_content(cls, content: str) -> WorldOverview:
        """Parse the content of the World Overview section from Tibia.com into an object of this class.

        Parameters
        ----------
        content:
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
            An instance of this class containing all the information.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the worlds section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        try:
            record_table, *tables = parsed_content.select("table.TableContent")
            m = record_regexp.search(record_table.text)
            return (WorldOverviewBuilder()
                    .record_count(parse_integer(m.group("count")))
                    .record_date(parse_tibia_datetime(m.group("date")))
                    .worlds(cls._parse_worlds_tables(tables))
                    .build())
        except (AttributeError, KeyError, ValueError) as e:
            raise InvalidContentError("content does not belong to the World Overview section in Tibia.com", e) from e

    @classmethod
    def _parse_worlds(cls, world_rows: List[bs4.Tag]) -> List[WorldEntry]:
        """Parse the world columns and adds the results to :py:attr:`worlds`.

        Parameters
        ----------
        world_rows: :class:`list` of :class:`bs4.Tag`
            A list containing the rows of each world.
        """
        worlds = []
        for world_row in world_rows:
            cols = world_row.select("td")
            name = cols[0].text.strip()
            is_online = True
            online_count = parse_integer(cols[1].text.strip(), None)
            if online_count is None:
                is_online = False
                online_count = 0

            location = try_enum(WorldLocation, clean_text(cols[2]))
            pvp = try_enum(PvpType, cols[3].text.strip())
            builder = (WorldEntryBuilder()
                       .name(name)
                       .location(location)
                       .pvp_type(pvp)
                       .online_count(online_count)
                       .is_online(is_online))
            # Check Battleye icon to get information
            battleye_icon = cols[4].select_one("span.HelperDivIndicator")
            if battleye_icon is not None and (m := battleye_regexp.search(battleye_icon["onmouseover"])):
                battleye_date = parse_tibia_full_date(m.group(1))
                builder.battleye_since(battleye_date).battleye_type(BattlEyeType.PROTECTED if battleye_date
                                                                    else BattlEyeType.INITIALLY_PROTECTED)

            additional_info = cols[5].text.strip()
            cls._parse_additional_info(builder, additional_info)
            worlds.append(builder.build())

        return worlds

    @classmethod
    def _parse_additional_info(cls, builder: WorldEntryBuilder, additional_info: str) -> None:
        if "blocked" in additional_info:
            builder.transfer_type(TransferType.BLOCKED)
        elif "locked" in additional_info:
            builder.transfer_type(TransferType.LOCKED)
        else:
            builder.transfer_type(TransferType.REGULAR)

        builder.is_experimental("experimental" in additional_info)
        builder.is_premium_only("premium" in additional_info)

    @classmethod
    def _parse_worlds_tables(cls, tables: List[bs4.Tag]) -> List[WorldEntry]:
        """Parse the tables and adds the results to the world list.

        Parameters
        ----------
        tables: :class:`map` of :class:`bs4.Tag`
            A mapping containing the tables with worlds.
        """
        worlds = []
        for _, worlds_table in zip(tables, tables[1:]):
            regular_world_rows = worlds_table.select("tr.Odd, tr.Even")
            worlds.extend(cls._parse_worlds(regular_world_rows))

        return worlds
