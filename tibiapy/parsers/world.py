"""Models related to the worlds section in Tibia.com."""
import re
from collections import OrderedDict
from typing import TYPE_CHECKING

from tibiapy import abc
from tibiapy.builders.world import (WorldBuilder, WorldEntryBuilder,
                                    WorldOverviewBuilder)
from tibiapy.enums import (BattlEyeType, PvpType,
                           TransferType, WorldLocation)
from tibiapy.errors import InvalidContent
from tibiapy.models import OnlineCharacter
from tibiapy.utils import (parse_integer, parse_tibia_datetime,
                           parse_tibia_full_date, parse_tibiacom_content,
                           try_enum)

if TYPE_CHECKING:
    import bs4

__all__ = (
    "WorldParser",
    "WorldOverviewParser",
)

record_regexp = re.compile(r'(?P<count>[\d.,]+) players \(on (?P<date>[^)]+)\)')
battleye_regexp = re.compile(r'since ([^.]+).')


class WorldParser:
    # region Public methods
    @classmethod
    def from_content(cls, content):
        """Parse a Tibia.com response into a :class:`World`.

        Parameters
        ----------
        content: :class:`str`
            The raw HTML from the server's information page.

        Returns
        -------
        :class:`World`
            The World described in the page, or :obj:`None`.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the world section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        try:
            error = tables.get("Error")
            if error and error[0].text == "World with this name doesn't exist!":
                return None
            selected_world = parsed_content.select_one('option:checked')
            builder = WorldBuilder().name(selected_world.text)
            cls._parse_world_info(builder, tables.get("World Information", []))

            online_table = tables.get("Players Online", [])
            for row in online_table[1:]:
                cols_raw = row.select('td')
                name, level, vocation = (c.text.replace('\xa0', ' ').strip() for c in cols_raw)
                builder.add_online_player(OnlineCharacter(name=name, level=int(level), vocation=vocation))
        except AttributeError:
            raise InvalidContent("content is not from the world section in Tibia.com")
        return builder.build()
    # endregion

    # region Private methods
    @classmethod
    def _parse_world_info(cls, builder: WorldBuilder, world_info_table):
        """
        Parse the World Information table from Tibia.com and adds the found values to the object.

        Parameters
        ----------
        world_info_table: :class:`list`[:class:`bs4.Tag`]
        """
        world_info = {}
        for row in world_info_table:
            cols_raw = row.select('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            world_info[field] = value
        try:
            builder.online_count(parse_integer(world_info.pop("players_online")))
        except KeyError:
            builder.online_count(0)
        builder.online(world_info["status"].lower() == "online")\
            .location(try_enum(WorldLocation, world_info.pop("location")))\
            .pvp_type(try_enum(PvpType, world_info.pop("pvp_type")))\
            .transfer_type(try_enum(TransferType, world_info.pop("transfer_type", None), TransferType.REGULAR))
        if m := record_regexp.match(world_info.pop("online_record")):
            builder.record_count(parse_integer(m.group("count")))
            builder.record_date(parse_tibia_datetime(m.group("date")))
        if "world_quest_titles" in world_info:
            titles = [q.strip() for q in world_info.pop("world_quest_titles").split(",")]
            if "currently has no title" not in titles[0]:
                builder.world_quest_titles(titles)
        builder.experimental(world_info.pop("game_world_type", None) == "Experimental")
        cls._parse_battleye_status(builder, world_info.pop("battleye_status"))
        builder.premium_only("premium_type" in world_info)

        month, year = world_info.pop("creation_date").split("/")
        month = int(month)
        year = int(year)
        if year > 90:
            year += 1900
        else:
            year += 2000
        builder.creation_date(f"{year:d}-{month:02d}")

    @classmethod
    def _parse_battleye_status(cls, builder, battleye_string):
        """Parse the BattlEye string and applies the results.

        Parameters
        ----------
        battleye_string: :class:`str`
            String containing the world's Battleye Status.
        """
        if m := battleye_regexp.search(battleye_string):
            battleye_date = parse_tibia_full_date(m.group(1))
            builder.battleye_date(battleye_date)\
                .battleye_type(BattlEyeType.PROTECTED if battleye_date else BattlEyeType.INITIALLY_PROTECTED)
        else:
            builder.battleye_date(None)\
                .battleye_type(BattlEyeType.UNPROTECTED)

    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parse the information tables found in a world's information page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[:class:`str`, :class:`list`[:class:`bs4.Tag`]]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.select('div.TableContainer')
        output = OrderedDict()
        for table in tables:
            title = table.select_one("div.Text").text
            title = title.split("[")[0].strip()
            inner_table = table.select_one("div.InnerTableContainer")
            output[title] = inner_table.select("tr")
        return output
    # endregion


class WorldOverviewParser(abc.Serializable):
    @classmethod
    def from_content(cls, content):
        """Parse the content of the World Overview section from Tibia.com into an object of this class.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the World Overview page in Tibia.com

        Returns
        -------
        :class:`WorldOverview`
            An instance of this class containing all the information.

        Raises
        ------
        InvalidContent
            If the provided content is not the HTML content of the worlds section in Tibia.com
        """
        parsed_content = parse_tibiacom_content(content)
        try:
            record_table, *tables \
                = parsed_content.select("table.TableContent")
            m = record_regexp.search(record_table.text)
            return (WorldOverviewBuilder()
                    .record_count(parse_integer(m.group("count")))
                    .record_date(parse_tibia_datetime(m.group("date")))
                    .worlds(cls._parse_worlds_tables(tables))
                    .build())
        except (AttributeError, KeyError, ValueError) as e:
            raise InvalidContent("content does not belong to the World Overview section in Tibia.com", e)

    @classmethod
    def _parse_worlds(cls, world_rows):
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
            online = True
            online_count = parse_integer(cols[1].text.strip(), None)
            if online_count is None:
                online = False
                online_count = 0
            location = try_enum(WorldLocation, cols[2].text.replace("\u00a0", " ").strip())
            pvp = try_enum(PvpType, cols[3].text.strip())
            builder = (WorldEntryBuilder()
                       .name(name)
                       .location(location)
                       .pvp_type(pvp)
                       .online_count(online_count)
                       .online(online))
            # Check Battleye icon to get information
            battleye_icon = cols[4].select_one("span.HelperDivIndicator")
            if battleye_icon is not None:
                if m := battleye_regexp.search(battleye_icon["onmouseover"]):
                    battleye_date = parse_tibia_full_date(m.group(1))
                    builder.battleye_date(battleye_date).battleye_type(BattlEyeType.PROTECTED if battleye_date else BattlEyeType.INITIALLY_PROTECTED)
            additional_info = cols[5].text.strip()
            cls._parse_additional_info(builder, additional_info)
            worlds.append(builder.build())
        return worlds

    @classmethod
    def _parse_additional_info(cls, builder, additional_info):
        if "blocked" in additional_info:
            builder.transfer_type(TransferType.BLOCKED)
        elif "locked" in additional_info:
            builder.transfer_type(TransferType.LOCKED)
        else:
            builder.transfer_type(TransferType.REGULAR)
        builder.experimental("experimental" in additional_info)
        builder.premium_only("premium" in additional_info)

    @classmethod
    def _parse_worlds_tables(cls, tables):
        """Parse the tables and adds the results to the world list.

        Parameters
        ----------
        tables: :class:`map` of :class:`bs4.Tag`
            A mapping containing the tables with worlds.
        """
        worlds = []
        for title_table, worlds_table in zip(tables, tables[1:]):
            regular_world_rows = worlds_table.select("tr.Odd, tr.Even")
            worlds.extend(cls._parse_worlds(regular_world_rows))
        return worlds