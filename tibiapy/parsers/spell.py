"""Parsers for the spell sections and spell pages."""
from __future__ import annotations

import os
import re
import urllib.parse
from typing import Dict, Optional, TYPE_CHECKING

import bs4

from tibiapy import errors
from tibiapy.builders.spell import RuneBuilder, SpellBuilder, SpellEntryBuilder, SpellSectionBuilder
from tibiapy.enums import SpellGroup, SpellSorting, SpellType, SpellVocationFilter
from tibiapy.utils import (get_rows, parse_form_data, parse_integer, parse_link_info, parse_tibiacom_content,
                           parse_tibiacom_tables, try_enum)

if TYPE_CHECKING:
    from tibiapy.models import Rune, Spell, SpellsSection

__all__ = (
    "SpellsSectionParser",
    "SpellParser",
)

spell_name = re.compile(r"([^(]+)\(([^)]+)\)")
group_pattern = re.compile(r"(?P<group>\w+)(?:\s?\(Secondary Group: (?P<secondary>[^)]+))?")
cooldown_pattern = re.compile(
    r"(?P<cooldown>\d+)s\s?\(Group: (?P<group_cooldown>\d+)s(?:,\s?"
    r"Secondary Group: (?P<secondary_group_cooldown>\d+))?",
)


class SpellsSectionParser:
    """Parses Tibia.com content from the Spells Section."""

    @classmethod
    def from_content(cls, content: str) -> SpellsSection:
        """Parse the content of the spells section.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The spells contained and the filtering information.

        Raises
        ------
        InvalidContent
            If content is not the HTML of the spells section.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            table_content_container = parsed_content.select_one("div.InnerTableContainer")
            spells_table = table_content_container.find("table", class_=lambda t: t != "TableContent")
            spell_rows = spells_table.find_all("tr", {"bgcolor": ["#D4C0A1", "#F1E0C6"]})
            builder = SpellSectionBuilder()
            for row in spell_rows:
                columns = row.select("td")
                if len(columns) != 7:
                    continue

                spell_link = columns[0].select_one("a")
                link_info = parse_link_info(spell_link)
                cols_text = [c.text for c in columns]
                identifier = link_info["query"]["spell"]
                match = spell_name.findall(cols_text[0])
                name, words = match[0]
                group = try_enum(SpellGroup, cols_text[1])
                spell_type = try_enum(SpellType, cols_text[2])
                level = parse_integer(cols_text[3], None)
                mana = parse_integer(cols_text[4], None)
                price = parse_integer(cols_text[5], 0)
                premium = "yes" in cols_text[6]
                spell = (SpellEntryBuilder()
                         .name(name.strip())
                         .words(words.strip())
                         .spell_type(spell_type)
                         .exp_level(level)
                         .group(group)
                         .mana(mana)
                         .is_premium(premium)
                         .price(price)
                         .identifier(identifier)).build()
                builder.add_entry(spell)

            form = parsed_content.select_one("form")
            data = parse_form_data(form)
            builder.vocation(try_enum(SpellVocationFilter, data.values["vocation"]))
            builder.group(try_enum(SpellGroup, data.values["group"]))
            builder.premium(try_enum(SpellGroup, data.values["group"]))
            builder.spell_type(try_enum(SpellType, data.values["type"]))
            builder.sort_by(try_enum(SpellSorting, data.values["sort"]))
            builder.premium("yes" in data.values["premium"] if data.values["premium"] else None)
            return builder.build()
        except (AttributeError, TypeError, KeyError) as e:
            raise errors.InvalidContentError("content does not belong to the Spells section", e) from e


class SpellParser:
    """Parses Tibia.com from a spell's information page."""

    @classmethod
    def from_content(cls, content: str) -> Optional[Spell]:
        """Parse the content of a spells page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The spell data. If the spell doesn't exist, this will be :obj:`None`.

        Raises
        ------
        InvalidContent
            If content is not the HTML of the spells section.
        """
        parsed_content = parse_tibiacom_content(content)
        tables = parse_tibiacom_tables(parsed_content)
        title_table = parsed_content.find("table", attrs={"class": False})
        if "Spell Information" not in tables:
            if "Spells" in tables:
                return None

            raise errors.InvalidContentError("content is not a spell page.")

        spell_table = tables["Spell Information"]
        img = title_table.select_one("img")
        url = urllib.parse.urlparse(img["src"])
        filename = os.path.basename(url.path)
        identifier = str(filename.split(".")[0])
        builder = SpellBuilder().identifier(identifier)
        cls._parse_spells_table(builder, spell_table)
        builder.description(cls._parse_description(title_table))
        if "Rune Information" in tables:
            builder.rune(cls._parse_rune_table(tables["Rune Information"]))

        return builder.build()

    @classmethod
    def _parse_description(cls, title_table: bs4.Tag) -> str:
        next_sibling = title_table.next_sibling
        description = ""
        while next_sibling:
            if isinstance(next_sibling, bs4.Tag):
                if next_sibling.name == "br":
                    description += "\n"
                elif next_sibling.name in ["table", "div"]:
                    break

            else:
                description += next_sibling.text

            next_sibling = next_sibling.next_sibling

        return description.strip()

    @classmethod
    def _parse_rune_table(cls, table: bs4.Tag) -> Rune:
        """Parse the rune information table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the rune information.

        Returns
        -------
        :class:`Rune`
            The rune described in the table.
        """
        attrs = cls._parse_table_attributes(table)
        return (RuneBuilder().name(attrs["name"])
                .group(try_enum(SpellGroup, attrs["group"]))
                .vocations([v.strip() for v in attrs["vocation"].split(",")])
                .magic_type(attrs.get("magic_type"))
                .magic_level(parse_integer(attrs.get("mag_lvl"), 0))
                .exp_level(parse_integer(attrs.get("exp_lvl"), 0))
                .mana(parse_integer(attrs.get("mana"), None))
                .build())

    @classmethod
    def _parse_spells_table(cls, builder: SpellBuilder, spell_table: bs4.Tag) -> None:
        """Parse the table containing spell information.

        Parameters
        ----------
        builder: :class:`SpellBuilder`
            The instance of the builder where data will be collected.
        spell_table: :class:`bs4.Tag`
            The table containing the spell information.
        """
        attrs = cls._parse_table_attributes(spell_table)
        builder.name(attrs["name"])
        builder.words(attrs["formula"])
        builder.is_premium("yes" in attrs["premium"])
        builder.exp_level(parse_integer(attrs["exp_lvl"], None))
        builder.vocations([s.strip() for s in attrs["vocation"].split(",")])
        builder.cities([s.strip() for s in attrs["city"].split(",")] if "none" not in attrs["city"] else [])
        m = group_pattern.match(attrs["group"])
        groups = m.groupdict()
        builder.group(try_enum(SpellGroup, groups.get("group")))
        builder.group_secondary(groups.get("secondary"))
        m = cooldown_pattern.match(attrs["cooldown"])
        cooldowns = m.groupdict()
        builder.cooldown(int(cooldowns["cooldown"]))
        builder.cooldown_group(int(cooldowns["group_cooldown"]))
        builder.cooldown_group_secondary(parse_integer(cooldowns.get("secondary_group_cooldown"), None))
        builder.spell_type(try_enum(SpellType, attrs["type"]))
        builder.soul_points(parse_integer(attrs.get("soul_points"), None))
        builder.mana(parse_integer(attrs.get("mana"), None))
        builder.amount(parse_integer(attrs.get("amount"), None))
        builder.price(parse_integer(attrs.get("price"), 0))
        builder.magic_type(attrs.get("magic_type"))

    @classmethod
    def _parse_table_attributes(cls, table: bs4.Tag) -> Dict[str, str]:
        """Parse the attributes of a table.

        Create a dictionary where every key is the left column (cleaned up) and the value is the right column.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table to get the attributes from.

        Returns
        -------
        :class:`dict`
            The table attributes.
        """
        spell_rows = get_rows(table)
        attrs = {}
        for row in spell_rows:
            cols = row.select("td")
            cols_text = [c.text for c in cols]
            clean_name = cols_text[0].replace(":", "").replace(" ", "_").lower().strip()
            value = cols_text[1]
            attrs[clean_name] = value

        return attrs
