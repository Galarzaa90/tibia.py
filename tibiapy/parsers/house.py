"""Models related to the houses section in Tibia.com."""
from __future__ import annotations
import datetime
import re
from typing import Optional, TYPE_CHECKING

import bs4

from tibiapy.builders.house import HousesSectionBuilder, HouseEntryBuilder, HouseBuilder
from tibiapy.enums import HouseOrder, HouseStatus, HouseType, Sex
from tibiapy.errors import InvalidContentError
from tibiapy.utils import (clean_text, get_rows, parse_tibia_datetime, parse_tibia_money, parse_tibiacom_content,
                           parse_tibiacom_tables,
                           try_enum, parse_form_data)

if TYPE_CHECKING:
    from tibiapy.models import HousesSection, House

__all__ = (
    "HousesSectionParser",
    "HouseParser",
)

id_regex = re.compile(r"house_(\d+)\.")
bed_regex = re.compile(r"This (?P<type>\w+) can have up to (?P<beds>[\d-]+) bed")
info_regex = (
    re.compile(r"The (?:house|guildhall) has a size of (?P<size>\d+) square meters?. "
               r"The monthly rent is (?P<rent>\d+k+) gold and will be debited to the bank account on (?P<world>\w+).")
)

rented_regex = re.compile(r"The (?:house|guildhall) has been rented by (?P<owner>[^.]+)\."
                          r" (?P<pronoun>\w+) has paid the rent until (?P<paid_until>[^.]+)\.")
transfer_regex = re.compile(r"\w+ will move out on (?P<transfer_date>[^(]+)\([^)]+\)(?: and (?P<verb>wants to|will)"
                            r" pass the (?:house|guildhall) to (?P<transferee>[\w\s]+) for "
                            r"(?P<transfer_price>\d+) gold coin)?")
moving_regex = re.compile(r"\w+ will move out on (?P<move_date>[^(]+)")
bid_regex = (
    re.compile(r"The highest bid so far is (?P<highest_bid>\d+) gold and has been submitted by (?P<bidder>[^.]+)")
)
auction_regex = re.compile(r"The auction (?P<auction_state>has ended|will end) at (?P<auction_end>[^.]+).")

list_header_regex = re.compile(r"Available (?P<type>[\w\s]+) in (?P<town>[\w\s']+) on (?P<world>\w+)")
list_auction_regex = re.compile(r"\((?P<bid>\d+) gold; (?P<time_left>\w)+ (?P<time_unit>day|hour)s? left\)")


class HousesSectionParser:
    """Parser for the houses section from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> HousesSection:
        """Parse the content of a house list from Tibia.com into a list of houses.

        Parameters
        ----------
        content:
            The raw HTML response from the house list.

        Returns
        -------
            The houses found in the page.

        Raises
        ------
        InvalidContent
            Content is not the house list from Tibia.com
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parse_tibiacom_tables(parsed_content)
            builder = HousesSectionBuilder()
            if "House Search" not in tables:
                raise InvalidContentError("content does not belong to the houses section")

            form = parsed_content.select_one("div.BoxContent > form")
            cls._parse_filters(builder, form)
            if len(tables) < 2:
                return builder.build()

            houses_table = tables[next(iter(tables.keys()))]
            _, *rows = get_rows(houses_table)
            for row in rows[1:]:
                cols = row.select("td")
                if len(cols) != 5:
                    continue

                name = clean_text(cols[0])
                house_builder = (HouseEntryBuilder()
                                 .name(name)
                                 .world(builder._world)
                                 .town(builder._town)
                                 .type(builder._house_type))
                size = cols[1].text.replace("sqm", "")
                house_builder.size(int(size))
                rent = cols[2].text.replace("gold", "")
                house_builder.rent(parse_tibia_money(rent))
                status = clean_text(cols[3])
                cls._parse_status(house_builder, status)
                id_input = cols[4].select_one("input[name=houseid]")
                house_builder.id(int(id_input["value"]))
                builder.add_entry(house_builder.build())

            return builder.build()
        except (ValueError, AttributeError, KeyError) as e:
            raise InvalidContentError("content does not belong to a Tibia.com house list", e) from e

    @classmethod
    def _parse_filters(cls, builder: HousesSectionBuilder, form: bs4.Tag) -> None:
        form_data = parse_form_data(form)
        builder.available_worlds(list(form_data.available_options["world"].values()))
        builder.available_towns(list(form_data.available_options["town"].values()))
        builder.world(form_data.values["world"])
        builder.town(form_data.values["town"])
        builder.status(try_enum(HouseStatus, form_data.values.get("state")))
        builder.house_type(try_enum(HouseType, form_data.values.get("type", "")[:-1]))
        builder.order(try_enum(HouseOrder, form_data.values.get("order"), HouseOrder.NAME))

    @classmethod
    def _parse_status(cls, builder: HouseEntryBuilder, status: str) -> None:
        """Parse the status string found in the table and applies the corresponding values.

        Parameters
        ----------
        builder: :class:`HouseEntryBuilder`
            The instance of the builder where data will be collected.
        status: :class:`str`
            The string containing the status.
        """
        if "rented" in status:
            builder.status(HouseStatus.RENTED)
        else:
            if m := list_auction_regex.search(status):
                builder.highest_bid(int(m.group("bid")))
                if m.group("time_unit") == "day":
                    builder.time_left(datetime.timedelta(days=int(m.group("time_left"))))
                else:
                    builder.time_left(datetime.timedelta(hours=int(m.group("time_left"))))

            builder.status(HouseStatus.AUCTIONED)


class HouseParser:
    """Parser for Houses information."""

    # region Public methods
    @classmethod
    def from_content(cls, content: str) -> Optional[House]:
        """Parse a Tibia.com response into a House object.

        Parameters
        ----------
        content:
            HTML content of the page.

        Returns
        -------
            The house contained in the page, or None if the house doesn't exist.

        Raises
        ------
        InvalidContent
            If the content is not the house section on Tibia.com
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            image_column, desc_column, *_ = parsed_content.select("td")
            if "No information" in image_column.text:
                return None

            image = image_column.select_one("img")
            for br in desc_column.select("br"):
                br.replace_with("\n")

            description = clean_text(desc_column).replace("\n\n", "\n")
            lines = description.splitlines()
            try:
                name, beds, info, state, *_ = lines
            except ValueError as e:
                raise InvalidContentError("content does is not from the house section of Tibia.com") from e

            image_url = image["src"]
            builder = (HouseBuilder()
                       .name(name.strip())
                       .image_url(image_url)
                       .id(int(id_regex.search(image_url).group(1))))
            if m := bed_regex.search(beds):
                if m.group("type").lower() in ["guildhall", "clanhall"]:
                    builder.type(HouseType.GUILDHALL)
                else:
                    builder.type(HouseType.HOUSE)

                builder.beds(int(m.group("beds")))

            if m := info_regex.search(info):
                builder.world(m.group("world"))
                builder.rent(parse_tibia_money(m.group("rent")))
                builder.size(int(m.group("size")))

            cls._parse_status(builder, state)
            return builder.build()
        except (ValueError, TypeError) as e:
            raise InvalidContentError("content does not belong to a house page", e) from e

    # endregion

    @classmethod
    def _parse_status(cls, builder: HouseBuilder, status: str) -> None:
        """Parse the house's state description and applies the corresponding values.

        Parameters
        ----------
        builder: :class:`HouseBuilder`
            The instance of the builder where data will be collected.
        status: :class:`str`
            Plain text string containing the current renting state of the house.
        """
        if m := rented_regex.search(status):
            builder.status(HouseStatus.RENTED)
            builder.owner(m.group("owner"))
            builder.owner_sex(Sex.MALE if m.group("pronoun") == "He" else Sex.FEMALE)
            builder.paid_until(parse_tibia_datetime(m.group("paid_until")))
        else:
            builder.status(HouseStatus.AUCTIONED)

        if m := transfer_regex.search(status):
            builder.transfer_date(parse_tibia_datetime(m.group("transfer_date")))
            builder.transfer_accepted(m.group("verb") == "will")
            builder.transfer_recipient(m.group("transferee"))
            price = m.group("transfer_price")
            builder.transfer_price(int(price) if price is not None else 0)

        if m := auction_regex.search(status):
            builder.auction_end(parse_tibia_datetime(m.group("auction_end")))

        if m := bid_regex.search(status):
            builder.highest_bid(int(m.group("highest_bid")))
            builder.highest_bidder(m.group("bidder"))
