"""Models related to the guilds section in Tibia.com."""
from __future__ import annotations

import datetime
import re
from typing import Dict, Optional, TYPE_CHECKING, Tuple

from tibiapy.builders import GuildBuilder, GuildWarEntryBuilder, GuildWarsBuilder
from tibiapy.errors import InvalidContentError
from tibiapy.models import GuildEntry, GuildHouse, GuildInvite, GuildMember, GuildWarEntry, GuildsSection
from tibiapy.utils import clean_text, parse_form_data, parse_link_info, parse_tibia_date, parse_tibiacom_content

if TYPE_CHECKING:
    import bs4
    from tibiapy.models import Guild, GuildWars

__all__ = (
    "GuildParser",
    "GuildsSectionParser",
    "GuildWarsParser",
)

COLS_INVITED_MEMBER = 2
COLS_GUILD_MEMBER = 6

founded_regex = re.compile(
    r"(?P<desc>.*)The guild was founded on (?P<world>\w+) on (?P<date>[^.]+)\.\nIt is (?P<status>[^.]+).",
    re.DOTALL,
)
applications_regex = re.compile(r"Guild is (\w+) for applications\.")
homepage_regex = re.compile(r"The official homepage is at ([\w.]+)\.")
guildhall_regex = re.compile(r"Their home on \w+ is (?P<name>[^.]+). The rent is paid until (?P<date>[^.]+)")
disband_regex = re.compile(r"It will be disbanded on (\w+\s\d+\s\d+)\s([^.]+).")
disband_tibadata_regex = re.compile(r"It will be disbanded, ([^.]+).")
title_regex = re.compile(r"([^(]+)\(([^)]+)\)")

war_guilds_regegx = re.compile(r"The guild ([\w\s]+) is at war with the guild ([^.]+).")
war_score_regex = re.compile(r"scored ([\d,]+) kills? against")
war_fee_regex = re.compile(r"the guild [\w\s]+ wins the war, they will receive ([\d,]+) gold.")
war_score_limit_regex = re.compile(r"guild scores ([\d,]+) kills against")
war_end_regex = re.compile(r"war will end on (\w{3}\s\d{2}\s\d{4})")

war_history_header_regex = re.compile(r"guild ([\w\s]+) fought against ([\w\s]+).")
war_start_duration_regex = re.compile(r"started on (\w{3}\s\d{2}\s\d{4}) and had been set for a duration of (\w+) days")
kills_needed_regex = re.compile(r"(\w+) kills were needed")
war_history_fee_regex = re.compile(r"agreed on a fee of (\w+) gold for the guild [\w\s]+ and a fee of (\d+) gold")
surrender_regex = re.compile(r"(?:The guild ([\w\s]+)|A disbanded guild) surrendered on (\w{3}\s\d{2}\s\d{4})")
war_ended_regex = re.compile(r"war ended on (\w{3}\s\d{2}\s\d{4}) when the guild ([\w\s]+) had reached the")
war_score_end_regex = re.compile(r"scored (\d+) kills against")

war_current_empty = re.compile(r"The guild ([\w\s]+) is currently not")


class GuildsSectionParser:
    """Parser for the guild sections in Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> Optional[GuildsSection]:
        """Get a list of guilds from the HTML content of the world guilds' page.

        Parameters
        ----------
        content:
            The HTML content of the page.

        Returns
        -------
            List of guilds in the current world. :obj:`None` if it's the list of a world that doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a guild's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            form = parsed_content.select_one("form")
            data = parse_form_data(form)
            selected_world = data.values["world"] or None
            available_worlds = [w for w in data.available_options["world"].values() if w]
            guilds = GuildsSection(world=selected_world, available_worlds=available_worlds)
        except (AttributeError, KeyError) as e:
            raise InvalidContentError("Content does not belong to world guild list.", e) from e
        # First TableContainer contains world selector.
        _, *containers = parsed_content.select("div.TableContainer")
        for container in containers:
            header = container.select_one("div.Text")
            active = "Active" in header.text
            header, *rows = container.find_all("tr", {"bgcolor": ["#D4C0A1", "#F1E0C6"]})
            for row in rows:
                columns = row.select("td")
                logo_img = columns[0].select_one("img")["src"]
                description_lines = columns[1].get_text("\n").split("\n", 1)
                name = description_lines[0]
                description = None
                if len(description_lines) > 1:
                    description = description_lines[1].replace("\r", "").replace("\n", " ")

                guild = GuildEntry(name=name, world=guilds.world, logo_url=logo_img, description=description,
                                   active=active)
                guilds.entries.append(guild)

        return guilds


class GuildParser:
    """Parser for guild pages in Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> Optional[Guild]:
        """Create an instance of the class from the HTML content of the guild's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
            The guild contained in the page or None if it doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a guild's page.
        """
        if "An internal error has occurred" in content:
            return None

        parsed_content = parse_tibiacom_content(content)
        try:
            name_header = parsed_content.select_one("h1")
            builder = GuildBuilder().name(name_header.text.strip())
        except AttributeError as e:
            raise InvalidContentError("content does not belong to a Tibia.com guild page.", e) from e

        cls._parse_logo(builder, parsed_content)
        info_container = parsed_content.select_one("#GuildInformationContainer")
        cls._parse_guild_info(builder, info_container)
        cls._parse_application_info(builder, info_container)
        cls._parse_guild_homepage(builder, info_container)
        cls._parse_guild_guildhall(builder, info_container)
        cls._parse_guild_disband_info(builder, info_container)
        cls._parse_guild_members(builder, parsed_content)

        return builder.build()

    # endregion

    # region Private methods
    @classmethod
    def _parse_current_member(
            cls,
            builder: GuildBuilder,
            previous_rank: Dict[int, str],
            values: Tuple[str, ...],
    ) -> None:
        """Parse the column texts of a member row into a member dictionary.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        previous_rank: :class:`dict`[int, str]
            The last rank present in the rows.
        values: :class:`tuple` of :class:`str`
            A list of row contents.
        """
        rank, name, vocation, level, joined, status = values
        rank = rank or previous_rank[1]
        title = None
        previous_rank[1] = rank
        if m := title_regex.match(name):
            name = m.group(1)
            title = m.group(2)

        joined = parse_tibia_date(joined)
        builder.add_member(GuildMember(name=name.strip(), rank=rank.strip(), title=title, level=int(level),
                                       vocation=vocation, joined_on=joined, is_online=status == "online"))

    @classmethod
    def _parse_application_info(cls, builder: GuildBuilder, info_container: bs4.Tag) -> None:
        """Parse the guild's application info.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        if m := applications_regex.search(info_container.text):
            builder.open_applications(m.group(1) == "opened")

        builder.active_war("during war" in info_container.text)

    @classmethod
    def _parse_guild_disband_info(cls, builder: GuildBuilder, info_container: bs4.Tag) -> None:
        """Parse the guild's disband info, if available.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        if m := disband_regex.search(info_container.text):
            builder.disband_condition(m.group(2))
            builder.disband_date(parse_tibia_date(clean_text(m.group(1))))

    @classmethod
    def _parse_guild_guildhall(cls, builder: GuildBuilder, info_container: bs4.Tag) -> None:
        """Parse the guild's guildhall info.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        if m := guildhall_regex.search(info_container.text):
            paid_until = parse_tibia_date(clean_text(m.group("date")))
            builder.guildhall(GuildHouse(name=m.group("name"), paid_until=paid_until))

    @classmethod
    def _parse_guild_homepage(cls, builder: GuildBuilder, info_container: bs4.Tag) -> None:
        """Parse the guild's homepage info.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        if m := homepage_regex.search(info_container.text):
            builder.homepage(m.group(1))

        if link := info_container.select_one("a"):
            link_info = parse_link_info(link)
            if "target" in link_info["query"]:
                builder.homepage(link_info["query"]["target"])
            else:
                builder.homepage(link_info["url"])

    @classmethod
    def _parse_guild_info(cls, builder: GuildBuilder, info_container: bs4.Tag) -> None:
        """Parse the guild's general information and applies the found values.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        if m := founded_regex.search(info_container.text):
            description = m.group("desc").strip()
            builder.description(description or None)
            builder.world(m.group("world"))
            builder.founded(parse_tibia_date(clean_text(m.group("date"))))
            builder.active("currently active" in m.group("status"))

    @classmethod
    def _parse_logo(cls, builder: GuildBuilder, parsed_content: bs4.Tag) -> bool:
        """Parse the guild logo and saves it to the instance.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        parsed_content: :class:`bs4.Tag`
            The parsed content of the page.

        Returns
        -------
        :class:`bool`
            Whether the logo was found or not.
        """
        logo_img = parsed_content.select_one('img[height="64"]')
        if logo_img is None:
            raise InvalidContentError("content does not belong to a Tibia.com guild page.")

        builder.logo_url(logo_img["src"])

    @classmethod
    def _parse_guild_members(cls, builder: GuildBuilder, parsed_content: bs4.Tag) -> None:
        """Parse the guild's member and invited list.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        parsed_content: :class:`bs4.Tag`
            The parsed content of the guild's page
        """
        member_rows = parsed_content.find_all("tr", {"bgcolor": ["#D4C0A1", "#F1E0C6"]})
        previous_rank = {}
        for row in member_rows:
            columns = row.select("td")
            values = tuple(clean_text(c) for c in columns)
            if len(columns) == COLS_GUILD_MEMBER:
                cls._parse_current_member(builder, previous_rank, values)

            if len(columns) == COLS_INVITED_MEMBER:
                cls._parse_invited_member(builder, values)

    @classmethod
    def _parse_invited_member(cls, builder: GuildBuilder, values: tuple[str, ...]) -> None:
        """Parse the column texts of an invited row into a invited dictionary.

        Parameters
        ----------
        builder: :class:`GuildBuilder`
            The builder where data will be stored to.
        values: tuple[:class:`str`]
            A list of row contents.
        """
        name, date = values
        if date != "Invitation Date":
            date = parse_tibia_date(date)
            builder.add_invite(GuildInvite(name=name, invited_on=date))
    # endregion


class GuildWarsParser:
    """Parser for guild war history from Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> GuildWars:
        """Get a guild's war information from Tibia.com's content.

        Parameters
        ----------
        content:
            The HTML content of a guild's war section in Tibia.com

        Returns
        -------
            The guild's war information.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            table_current, table_history = parsed_content.select("div.TableContainer")
            current_table_content = table_current.select_one("table.TableContent")
            current_war = None
            builder = GuildWarsBuilder()
            if current_table_content is not None:
                for br in current_table_content.select("br"):
                    br.replace_with("\n")

                current_war = cls._parse_current_war_information(current_table_content.text)
                builder.current(current_war)
            else:
                current_war_text = table_current.text
                current_war_match = war_current_empty.search(current_war_text)
                builder.name(current_war_match.group(1))

            history_entries = []
            history_contents = table_history.select("table.TableContent")
            for history_content in history_contents:
                for br in history_content.select("br"):
                    br.replace_with("\n")

                entry = cls._parse_war_history_entry(history_content.text)
                history_entries.append(entry)

            builder.history(history_entries)
            if current_war:
                builder.name(current_war.guild_name)
            elif history_entries:
                builder.name(history_entries[0].guild_name)

            return builder.build()
        except ValueError as e:
            raise InvalidContentError("content does not belong to the guild wars section", e) from e

    @classmethod
    def _parse_current_war_information(cls, text: str) -> GuildWarEntry:
        """Parse the guild's current war information.

        Parameters
        ----------
        text: :class:`str`
            The text describing the current war's information.

        Returns
        -------
        :class:`GuildWarEntry`
            The guild's war entry for the current war.
        """
        text = clean_text(text)
        names_match = war_guilds_regegx.search(text)
        guild_name, opposing_name = names_match.groups()
        builder = GuildWarEntryBuilder().guild_name(guild_name).opponent_name(opposing_name)
        scores_match = war_score_regex.findall(text)
        guild_score, opposing_score = scores_match
        builder.guild_score(guild_score).opponent_score(opposing_score)
        fee_match = war_fee_regex.findall(text)
        guild_fee, opposing_fee = fee_match
        builder.guild_fee(guild_fee).opponent_fee(opposing_fee)

        score_limit_match = war_score_limit_regex.search(text)
        builder.score_limit(score_limit_match.group(1))

        end_date_match = war_end_regex.search(text)
        end_date_str = end_date_match.group(1)
        builder.end_date(parse_tibia_date(end_date_str))

        return builder.build()

    @classmethod
    def _parse_war_history_entry(cls, text: str) -> GuildWarEntry:
        """Parse a guild's war information.

        Parameters
        ----------
        text: :class:`str`
            The text describing the war's information.

        Returns
        -------
        :class:`GuildWarEntry`
            The guild's war entry described in the text.
        """
        text = clean_text(text)
        header_match = war_history_header_regex.search(text)
        guild_name, opposing_name = header_match.groups()
        builder = GuildWarEntryBuilder().guild_name(guild_name).opponent_name(opposing_name)
        if "disbanded guild" in opposing_name:
            builder.opponent_name(None)

        start_duration_match = war_start_duration_regex.search(text)
        start_str, duration_str = start_duration_match.groups()
        builder.start_date(parse_tibia_date(start_str))
        builder.duration(datetime.timedelta(days=int(duration_str)))
        kills_match = kills_needed_regex.search(text)
        kills_needed = int(kills_match.group(1))
        builder.score_limit(kills_needed)
        fee_match = war_history_fee_regex.search(text)
        guild_fee, opponent_fee = fee_match.groups()
        builder.guild_fee(guild_fee).opponent_fee(opponent_fee)
        guild_score = opponent_score = 0
        winner = None
        if surrender_match := surrender_regex.search(text):
            surrending_guild = surrender_match.group(1)
            builder.end_date(parse_tibia_date(surrender_match.group(2)))
            winner = guild_name if surrending_guild != guild_name else opposing_name
            builder.surrender(True)

        war_score_match = war_score_regex.findall(text)
        if war_score_match and len(war_score_match) == 2:
            guild_score, opponent_score = war_score_match
            guild_score = int(guild_score)
            opponent_score = guild_score

        if war_end_match := war_ended_regex.search(text):
            builder.end_date(parse_tibia_date(war_end_match.group(1)))
            winning_guild = war_end_match.group(2)
            if "disbanded guild" in winning_guild:
                winning_guild = None

            winner = guild_name if winning_guild == guild_name else opposing_name
            loser_score_match = war_score_end_regex.search(text)
            loser_score = int(loser_score_match.group(1)) if loser_score_match else 0
            guild_score = kills_needed if guild_name == winner else loser_score
            opponent_score = kills_needed if guild_name != winner else loser_score

        if "no guild had reached the needed kills" in text:
            winner = guild_name if guild_score > opponent_score else opposing_name

        builder.opponent_score(opponent_score).guild_score(guild_score).winner(winner)
        return builder.build()
