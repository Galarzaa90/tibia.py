"""Models related to the Tibia.com character page."""
from __future__ import annotations

import re
from collections import OrderedDict
from typing import List, TYPE_CHECKING

from tibiapy.builders.character import CharacterBuilder
from tibiapy.enums import Sex, Vocation
from tibiapy.errors import InvalidContent
from tibiapy.models import Achievement, Character, AccountBadge, AccountInformation, OtherCharacter, DeathParticipant, \
    Death, GuildMembership, CharacterHouse
from tibiapy.utils import (parse_popup, parse_tibia_date, parse_tibia_datetime, parse_tibiacom_content, split_list,
                           try_enum, parse_link_info, clean_text, parse_integer)

if TYPE_CHECKING:
    import bs4

# Extracts the scheduled deletion date of a character."""
deleted_regexp = re.compile(r'([^,]+), will be deleted at (.*)')
# Extracts the death's level and killers.
death_regexp = re.compile(r'Level (?P<level>\d+) by (?P<killers>.*)\.</td>')
# From the killers list, filters out the assists.
death_assisted = re.compile(r'(?P<killers>.+)\.<br/>Assisted by (?P<assists>.+)')
# From a killer entry, extracts the summoned creature
death_summon = re.compile(r'(?P<summon>an? .+) of (?P<name>[^<]+)')
link_search = re.compile(r'<a[^>]+>[^<]+</a>')
# Extracts the contents of a tag
link_content = re.compile(r'>([^<]+)<')

house_regexp = re.compile(r'paid until (.*)')

title_regexp = re.compile(r'(.*)\((\d+) titles? unlocked\)')
badge_popup_regexp = re.compile(r"\$\(this\),\s+'([^']+)',\s+'([^']+)',")

traded_label = "(traded)"

__all__ = (
    "CharacterParser",
)


class CharacterParser:

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the html content of the character's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`Character`
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
        if "Character Information" in tables.keys():
            cls._parse_character_information(builder, tables["Character Information"])
        else:
            raise InvalidContent("content does not contain a tibia.com character information page.")
        builder.achievements(cls._parse_achievements(tables.get("Account Achievements", [])))
        if "Account Badges" in tables:
            builder.account_badges(cls._parse_badges(tables["Account Badges"]))
        cls._parse_deaths(builder, tables.get("Character Deaths", []))
        builder.account_information(cls._parse_account_information(tables.get("Account Information", [])))
        builder.other_characters(cls._parse_other_characters(tables.get("Characters", [])))
        return builder.build()

    @classmethod
    def _parse_account_information(cls, rows):
        """Parse the character's account information.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`, optional
            A list of all rows contained in the table.
        """
        acc_info = {}
        if not rows:
            return
        for row in rows:
            cols_raw = row.select('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            acc_info[field] = value
        created = parse_tibia_datetime(acc_info["created"])
        loyalty_title = None if acc_info["loyalty_title"] == "(no title)" else acc_info["loyalty_title"]
        position = acc_info.get("position")
        return AccountInformation(created=created, loyalty_title=loyalty_title, position=position)

    @classmethod
    def _parse_achievements(cls, rows):
        """Parse the character's displayed achievements.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`
            A list of all rows contained in the table.
        """
        achievements = []
        for row in rows:
            cols = row.select('td')
            if len(cols) != 2:
                continue
            field, value = cols
            grade = str(field).count("achievement-grade-symbol")
            name = value.text.strip()
            secret_image = value.find("img")
            secret = False
            if secret_image:
                secret = True
            achievements.append(Achievement(name=name, grade=grade, is_secret=secret))
        return achievements

    @classmethod
    def _parse_badges(cls, rows: List[bs4.Tag]):
        """Parse the character's displayed badges.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`
            A list of all rows contained in the table.
        """
        row = rows[0]
        columns = row.select("td > span")
        account_badges = []
        for column in columns:
            popup_span = column.select_one("span.HelperDivIndicator")
            if not popup_span:
                # Badges are visible, but none selected.
                return []
            popup = parse_popup(popup_span['onmouseover'])
            name = popup[0]
            description = popup[1].text
            icon_image = column.select_one("img")
            icon_url = icon_image['src']
            account_badges.append(AccountBadge(name=name, icon_url=icon_url, description=description))
        return account_badges

    @classmethod
    def _parse_character_information(cls, builder: CharacterBuilder, rows):
        """
        Parse the character's basic information and applies the found values.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`
            A list of all rows contained in the table.
        """
        for row in rows:
            cols_raw = row.select('td')
            cols = [clean_text(ele) for ele in cols_raw]
            field, value = cols
            field = field.replace(":", "").lower()
            if field == "name":
                cls._parse_name_field(builder, value)
            elif field == "title":
                cls._parse_titles(builder, value)
            elif field == "former names":
                builder.former_names([fn.strip() for fn in value.split(",")])
            elif field == "former world":
                builder.former_world(value)
            elif field == "sex":
                builder.sex(try_enum(Sex, value))
            elif field == "vocation":
                builder.vocation(try_enum(Vocation, value))
            elif field == "level":
                builder.level(parse_integer(value))
            elif field == "achievement points":
                builder.achievement_points(parse_integer(value))
            elif field == "world":
                builder.world(value)
            elif field == "residence":
                builder.residence(value)
            elif field == "last login":
                if "never logged" in value.lower():
                    builder.last_login(None)
                else:
                    builder.last_login(parse_tibia_datetime(value))
            elif field == "position":
                builder.position(value)
            elif field == "comment":
                builder.comment(value)
            elif field == "account status":
                builder.is_premium("premium" in value.lower())
            elif field == "married to":
                builder.married_to(value)
            elif field == "house":
                cls._parse_house_column(builder, cols_raw[1])
            elif field == "guild membership":
                cls._parse_guild_column(builder, cols_raw[1])

    @classmethod
    def _parse_name_field(cls, builder: CharacterBuilder, value: str):
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
    def _parse_titles(cls, builder: CharacterBuilder, value: str):
        if m := title_regexp.match(value):
            name = m.group(1).strip()
            unlocked = int(m.group(2))
            if name == "None":
                name = None
            builder.title(name)
            builder.unlocked_titles(unlocked)

    @classmethod
    def _parse_house_column(cls, builder: CharacterBuilder, column: bs4.Tag):
        house_text = clean_text(column)
        m = house_regexp.search(house_text)
        paid_until = m.group(1)
        paid_until_date = parse_tibia_date(paid_until)
        house_link_tag = column.find('a')
        house_link = parse_link_info(house_link_tag)
        builder.add_house(
            CharacterHouse(
                id=house_link["query"]["houseid"],
                name=house_link["text"],
                town=house_link["query"]["town"],
                paid_until=paid_until_date,
                world=house_link["query"]["world"]
            )
        )

    @classmethod
    def _parse_guild_column(cls, builder: CharacterBuilder, column: bs4.Tag):
        guild_link = column.select_one('a')
        value = clean_text(column)
        rank = value.split("of the")[0]
        builder.guild_membership(GuildMembership(name=guild_link.text.replace("\xa0", " "), rank=rank.strip()))

    @classmethod
    def _parse_deaths(cls, builder: CharacterBuilder, rows):
        """Parse the character's recent deaths.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`
            A list of all rows contained in the table.
        """
        for row in rows:
            cols = row.select('td')
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
            killers_list = [cls._parse_killer(k) for k in killers_name_list]
            assists_list = [cls._parse_killer(k) for k in assists_name_list]
            builder.add_death(Death(
                level=level,
                killers=killers_list,
                assists=assists_list,
                time=death_time
            ))

    @classmethod
    def _parse_killer(cls, killer):
        """Parse a killer into a dictionary.

        Parameters
        ----------
        killer: :class:`str`
            The killer's raw HTML string.

        Returns
        -------
        :class:`dict`: A dictionary containing the killer's info.
        """
        # If the killer contains a link, it is a player.
        name = clean_text(killer)
        player = False
        traded = False
        summon = None
        if traded_label in killer:
            name = killer.replace('\xa0', ' ').replace(traded_label, "").strip()
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
    def _parse_other_characters(cls, rows):
        """Parse the character's other visible characters.

        Parameters
        ----------
        rows: :class:`list` of :class:`bs4.Tag`
            A list of all rows contained in the table.
        """
        other_characters = []
        for row in rows[1:]:
            cols_raw = row.select('td')
            cols = [ele.text.strip() for ele in cols_raw]
            if len(cols) != 4:
                continue
            name, world, status, *__ = cols
            _, *name = name.replace("\xa0", " ").split(" ")
            name = " ".join(name)
            traded = False
            if traded_label in name:
                name = name.replace(traded_label, "").strip()
                traded = True
            main_img = cols_raw[0].select_one('img')
            main = False
            if main_img and main_img['title'] == "Main Character":
                main = True
            position = None
            if "CipSoft Member" in status:
                position = "CipSoft Member"
            other_characters.append(OtherCharacter(name=name, world=world, is_online="online" in status,
                                                   is_deleted="deleted" in status, is_main=main, position=position,
                                                   is_traded=traded))
        return other_characters


    @classmethod
    def _parse_tables(cls, parsed_content):
        """
        Parse the information tables contained in a character's page.

        Parameters
        ----------
        parsed_content: :class:`bs4.BeautifulSoup`
            A :class:`BeautifulSoup` object containing all the content.

        Returns
        -------
        :class:`OrderedDict`[str, :class:`list`of :class:`bs4.Tag`]
            A dictionary containing all the table rows, with the table headers as keys.
        """
        tables = parsed_content.select('table[width="100%"]')
        output = OrderedDict()
        for table in tables:
            container = table.find_parent("div", {"class": "TableContainer"})
            if container:
                caption_container = container.select_one("div.CaptionContainer")
                title = caption_container.text.strip()
                offset = 0
            else:
                title = table.select_one("td").text.strip()
                offset = 1
            output[title] = table.select("tr")[offset:]
        return output
