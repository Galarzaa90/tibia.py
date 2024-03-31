"""Models related to the Tibia.com character page."""
from __future__ import annotations

import logging
import re
from collections import OrderedDict
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from tibiapy.builders import CharacterBuilder
from tibiapy.enums import Sex, Vocation
from tibiapy.errors import InvalidContentError
from tibiapy.models import (Achievement, Character, AccountBadge, AccountInformation, OtherCharacter, DeathParticipant,
                            Death, GuildMembership, CharacterHouse)
from tibiapy.utils import (get_rows, parse_popup, parse_tibia_date, parse_tibia_datetime, parse_tibiacom_content,
                           split_list,
                           try_enum, parse_link_info, clean_text, parse_integer)

if TYPE_CHECKING:
    import bs4

# Extracts the scheduled deletion date of a character."""
deleted_regexp = re.compile(r"([^,]+), will be deleted at (.*)")
# Extracts the death's level and killers.
death_regexp = re.compile(r"Level (?P<level>\d+) by (?P<killers>.*)\.</td>")
# From the killers list, filters out the assists.
death_assisted = re.compile(r"(?P<killers>.+)\.<br/>Assisted by (?P<assists>.+)")
# From a killer entry, extracts the summoned creature
death_summon = re.compile(r"(?P<summon>an? .+) of (?P<name>[^<]+)")
link_search = re.compile(r"<a[^>]+>[^<]+</a>")
# Extracts the contents of a tag
link_content = re.compile(r">([^<]+)<")

house_regexp = re.compile(r"paid until (.*)")

title_regexp = re.compile(r"(.*)\((\d+) titles? unlocked\)")
badge_popup_regexp = re.compile(r"\$\(this\),\s+'([^']+)',\s+'([^']+)',")

traded_label = "(traded)"

__all__ = (
    "CharacterParser",
)

logger = logging.getLogger(__name__)


class CharacterParser:
    """A parser for characters from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> Optional[Character]:
        """Create an instance of the class from the html content of the character's page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            The character contained in the page, or None if the character doesn't exist

        Raises
        ------
        InvalidContent
            If content is not the HTML of a character's page.
        """
        parsed_content = parse_tibiacom_content(content)
        tables = cls._parse_tables(parsed_content)
        builder = CharacterBuilder()
        if not tables:
            messsage_table = parsed_content.select_one("div.TableContainer")
            if messsage_table and "Could not find character" in messsage_table.text:
                return None

        table_parsers = {
            "Character Information": lambda t: cls._parse_character_information(builder, t),
            "Account Badges": lambda t: cls._parse_account_badges(builder, t),
            "Account Achievements": lambda t: cls._parse_achievements(builder, t),
            "Account Information": lambda t: cls._parse_account_information(builder, t),
            "Character Deaths": lambda t: cls._parse_deaths(builder, t),
            "Characters": lambda t: cls._parse_other_characters(builder, t),
        }

        if "Character Information" not in tables:
            raise InvalidContentError("content does not contain a tibia.com character information page.")

        for title, table in tables.items():
            if title in table_parsers:
                action = table_parsers[title]
                action(table)

        return builder.build()

    @classmethod
    def _parse_account_information(cls, builder: CharacterBuilder, rows: list[bs4.Tag]) -> None:
        """Parse the character's account information."""
        acc_info = {}

        for row in rows:
            cols_raw = row.select("td")
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = clean_text(field).replace(" ", "_").replace(":", "").lower()
            value = clean_text(value)
            acc_info[field] = value

        created = parse_tibia_datetime(acc_info["created"])
        loyalty_title = None if acc_info["loyalty_title"] == "(no title)" else acc_info["loyalty_title"]
        position = acc_info.get("position")
        builder.account_information(AccountInformation(created=created, loyalty_title=loyalty_title, position=position))

    @classmethod
    def _parse_achievements(cls, builder: CharacterBuilder, rows: List[bs4.Tag]) -> None:
        """Parse the character's displayed achievements."""
        for row in rows:
            cols = row.select("td")
            if len(cols) != 2:
                continue

            field, value = cols
            grade = str(field).count("achievement-grade-symbol")
            name = value.text.strip()
            secret_image = value.select_one("img")
            secret = secret_image is not None

            builder.add_achievement(Achievement(name=name, grade=grade, is_secret=secret))

    @classmethod
    def _parse_account_badges(cls, builder: CharacterBuilder, rows: List[bs4.Tag]) -> None:
        """Parse the character's displayed badges."""
        row = rows[0]
        columns = row.select("td > span")
        for column in columns:
            popup_span = column.select_one("span.HelperDivIndicator")
            popup = parse_popup(popup_span["onmouseover"])
            name = popup[0]
            description = popup[1].text
            icon_image = column.select_one("img")
            icon_url = icon_image["src"]
            builder.add_account_badge(AccountBadge(name=name, icon_url=icon_url, description=description))

    @classmethod
    def _parse_character_information(cls, builder: CharacterBuilder, rows: List[bs4.Tag]) -> None:
        """Parse the character's basic information and applies the found values."""
        field_actions: dict[str, Callable[[bs4.Tag, str], None]] = {
            "name": lambda rv, v: cls._parse_name_field(builder, v),
            "title": lambda rv, v: cls._parse_titles(builder, v),
            "former names": lambda rv, v: builder.former_names([fn.strip() for fn in v.split(",")]),
            "former world": lambda rv, v: builder.former_world(v),
            "sex": lambda rv, v: builder.sex(try_enum(Sex, v)),
            "vocation": lambda rv, v: builder.vocation(try_enum(Vocation, v)),
            "level": lambda rv, v: builder.level(parse_integer(v)),
            "achievement points": lambda rv, v: builder.achievement_points(parse_integer(v)),
            "world": lambda rv, v: builder.world(v),
            "residence": lambda rv, v: builder.residence(v),
            "last login": lambda rv, v: builder.last_login(None) if "never logged" in v.lower() else builder.last_login(
                parse_tibia_datetime(v),
            ),
            "position": lambda rv, v: builder.position(v),
            "comment": lambda rv, v: builder.comment(v),
            "account status": lambda rv, v: builder.is_premium("premium" in v.lower()),
            "married to": lambda rv, v: builder.married_to(v),
            "house": lambda rv, v: cls._parse_house_column(builder, rv),
            "guild membership": lambda rv, v: cls._parse_guild_column(builder, rv),
        }

        for row in rows:
            raw_field, raw_value = row.select("td")
            field, value = clean_text(raw_field), clean_text(raw_value)
            field = field.replace(":", "").lower()
            if field in field_actions:
                action = field_actions[field]
                action(raw_value, value)
            else:
                logger.debug("Unhandled character information field found: %s", field)

    @classmethod
    def _parse_name_field(cls, builder: CharacterBuilder, value: str) -> None:
        if m := deleted_regexp.match(value):
            value = m.group(1)
            builder.name(value)
            builder.deletion_date(parse_tibia_datetime(m.group(2)))
        else:
            builder.name(value)

        if traded_label in value:
            builder.name(value.replace(traded_label, "").strip())
            builder.traded(True)

    @classmethod
    def _parse_titles(cls, builder: CharacterBuilder, value: str) -> None:
        if m := title_regexp.match(value):
            name = m.group(1).strip()
            unlocked = int(m.group(2))
            if name == "None":
                name = None

            builder.title(name)
            builder.unlocked_titles(unlocked)

    @classmethod
    def _parse_house_column(cls, builder: CharacterBuilder, column: bs4.Tag) -> None:
        house_text = clean_text(column)
        m = house_regexp.search(house_text)
        paid_until = m.group(1)
        paid_until_date = parse_tibia_date(paid_until)
        house_link_tag = column.select_one("a")
        house_link = parse_link_info(house_link_tag)
        builder.add_house(
            CharacterHouse(
                id=int(house_link["query"]["houseid"]),
                name=house_link["text"],
                town=house_link["query"]["town"],
                paid_until=paid_until_date,
                world=house_link["query"]["world"],
            ),
        )

    @classmethod
    def _parse_guild_column(cls, builder: CharacterBuilder, column: bs4.Tag) -> None:
        guild_link = column.select_one("a")
        value = clean_text(column)
        rank = value.split("of the")[0]
        builder.guild_membership(GuildMembership(name=clean_text(guild_link), rank=rank.strip()))

    @classmethod
    def _parse_deaths(cls, builder: CharacterBuilder, rows: List[bs4.Tag]) -> None:
        """Parse the character's recent deaths."""
        for row in rows:
            cols = row.select("td")
            if len(cols) != 2:
                builder.deaths_truncated(True)
                break

            date_column, desc_column = cols
            death_time = parse_tibia_datetime(date_column.text)
            if not (death_info := death_regexp.search(str(desc_column))):
                continue

            level = int(death_info.group("level"))
            killers_desc = death_info.group("killers")
            assists_name_list = []
            # Check if the killers list contains assists
            if assist_match := death_assisted.search(killers_desc):
                # Filter out assists
                killers_desc = assist_match.group("killers")
                # Split assists into a list.
                assists_desc = assist_match.group("assists")
                assists_name_list = link_search.findall(assists_desc)

            killers_name_list = split_list(killers_desc)
            killers_list = [cls._parse_participant(k) for k in killers_name_list]
            assists_list = [cls._parse_participant(k) for k in assists_name_list]
            builder.add_death(Death(
                level=level,
                killers=killers_list,
                assists=assists_list,
                time=death_time,
            ))

    @classmethod
    def _parse_participant(cls, killer: str) -> DeathParticipant:
        """Parse a participant's information from their raw HTML string."""
        # If the killer contains a link, it is a player.
        name = clean_text(killer)
        player = False
        traded = False
        summon = None
        if traded_label in killer:
            name = clean_text(killer).replace(traded_label, "").strip()
            traded = True
            player = True

        if "href" in killer:
            m = link_content.search(killer)
            name = clean_text(m.group(1))
            player = True

        # Check if it contains a summon.
        if m := death_summon.search(name):
            summon = clean_text(m.group("summon"))
            name = clean_text(m.group("name"))

        return DeathParticipant(name=name, is_player=player, summon=summon, is_traded=traded)

    @classmethod
    def _parse_other_characters(cls, builder: CharacterBuilder, rows: List[bs4.Tag]) -> None:
        """Parse the character's other visible characters."""
        for row in rows[1:]:
            cols_raw = row.select("td")
            cols = [ele.text.strip() for ele in cols_raw]
            if len(cols) != 4:
                continue

            name, world, status, *__ = cols
            _, *name = clean_text(name).split(" ")
            name = " ".join(name)
            traded = False
            if traded_label in name:
                name = name.replace(traded_label, "").strip()
                traded = True

            main_img = cols_raw[0].select_one("img")
            main = False
            if main_img and main_img["title"] == "Main Character":
                main = True

            position = None
            if "CipSoft Member" in status:
                position = "CipSoft Member"

            builder.add_other_character(OtherCharacter(
                name=name,
                world=world,
                is_online="online" in status,
                is_deleted="deleted" in status,
                is_main=main,
                position=position,
                is_traded=traded,
            ))

    @classmethod
    def _parse_tables(cls, parsed_content: bs4.BeautifulSoup) -> Dict[str, List[bs4.Tag]]:
        """Parse the tables contained in a character's page and returns a mapping of their titles and rows."""
        tables = parsed_content.select('table[width="100%"]')
        output = OrderedDict()
        for table in tables:
            if container := table.find_parent("div", {"class": "TableContainer"}):
                caption_container = container.select_one("div.CaptionContainer")
                title = caption_container.text.strip()
                offset = 0
            else:
                title = table.select_one("td").text.strip()
                offset = 1

            output[title] = get_rows(table)[offset:]

        return output
