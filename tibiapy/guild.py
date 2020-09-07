import datetime
import re
from collections import defaultdict, OrderedDict
from typing import Dict, List, Optional

import bs4

from tibiapy import abc
from tibiapy.enums import Vocation
from tibiapy.errors import InvalidContent
from tibiapy.house import GuildHouse
from tibiapy.utils import parse_tibia_date, parse_tibiacom_content, try_date, try_datetime, try_enum

__all__ = (
    "Guild",
    "GuildMember",
    "GuildInvite",
    "GuildWars",
    "GuildWarEntry",
    "ListedGuild",
)

COLS_INVITED_MEMBER = 2
COLS_GUILD_MEMBER = 6

founded_regex = re.compile(
    r'(?P<desc>.*)The guild was founded on (?P<world>\w+) on (?P<date>[^.]+)\.\nIt is (?P<status>[^.]+).', re.DOTALL)
applications_regex = re.compile(r'Guild is (\w+) for applications\.')
homepage_regex = re.compile(r'The official homepage is at ([\w.]+)\.')
guildhall_regex = re.compile(r'Their home on \w+ is (?P<name>[^.]+). The rent is paid until (?P<date>[^.]+)')
disband_regex = re.compile(r'It will be disbanded on (\w+\s\d+\s\d+)\s([^.]+).')
disband_tibadata_regex = re.compile(r'It will be disbanded, ([^.]+).')
title_regex = re.compile(r'([\w\s]+)\s\(([^)]+)\)')

war_guilds_regegx = re.compile(r'The guild ([\w\s]+) is at war with the guild ([^.]+).')
war_score_regex = re.compile(r'scored ([\d,]+) kills? against')
war_fee_regex = re.compile(r'the guild [\w\s]+ wins the war, they will receive ([\d,]+) gold.')
war_score_limit_regex = re.compile(r'guild scores ([\d,]+) kills against')
war_end_regex = re.compile(r'war will end on (\w{3}\s\d{2}\s\d{4})')

war_history_header_regex = re.compile(r'guild ([\w\s]+) fought against ([\w\s]+).')
war_start_duration_regex = re.compile(r'started on (\w{3}\s\d{2}\s\d{4}) and had been set for a duration of (\w+) days')
kills_needed_regex = re.compile(r'(\w+) kills were needed')
war_history_fee_regex = re.compile(r'agreed on a fee of (\w+) gold for the guild [\w\s]+ and a fee of (\d+) gold')
surrender_regex = re.compile(r'(?:The guild ([\w\s]+)|A disbanded guild) surrendered on (\w{3}\s\d{2}\s\d{4})')
war_ended_regex = re.compile(r'war ended on (\w{3}\s\d{2}\s\d{4}) when the guild ([\w\s]+) had reached the')
war_score_end_regex = re.compile(r'scored (\d+) kills against')

war_current_empty = re.compile(r'The guild ([\w\s]+) is currently not')


class Guild(abc.BaseGuild, abc.Serializable):
    """
    Represents a Tibia guild.

    Attributes
    ------------
    name: :class:`str`
        The name of the guild.
    logo_url: :class:`str`
        The URL to the guild's logo.
    description: :class:`str`, optional
        The description of the guild.
    world: :class:`str`
        The world this guild belongs to.
    founded: :class:`datetime.date`
        The day the guild was founded.
    active: :class:`bool`
        Whether the guild is active or still in formation.
    guildhall: :class:`GuildHouse`, optional
        The guild's guildhall if any.
    open_applications: :class:`bool`
        Whether applications are open or not.
    active_war: :class:`bool`
        Whether the guild is currently in an active war or not.

        .. versionadded:: 3.0.0
    disband_date: :class:`datetime.datetime`, optional
        The date when the guild will be disbanded if the condition hasn't been meet.
    disband_condition: :class:`str`, optional
        The reason why the guild will get disbanded.
    homepage: :class:`str`, optional
        The guild's homepage, if any.
    members: :class:`list` of :class:`GuildMember`
        List of guild members.
    invites: :class:`list` of :class:`GuildInvite`
        List of invited characters.
    """
    __slots__ = (
        "world",
        "logo_url",
        "description",
        "founded",
        "active",
        "guildhall",
        "open_applications",
        "active_war",
        "disband_condition",
        "disband_date",
        "homepage",
        "members",
        "invites",
    )

    _serializable_properties = (
        "member_count",
        "online_count",
        "ranks"
    )

    def __init__(self, name=None, world=None, **kwargs):
        self.name: str = name
        self.world: str = world
        self.logo_url: str = kwargs.get("logo_url")
        self.description: Optional[str] = kwargs.get("description")
        self.founded = try_date(kwargs.get("founded"))
        self.active: bool = kwargs.get("active", False)
        self.guildhall: Optional[GuildHouse] = kwargs.get("guildhall")
        self.open_applications: bool = kwargs.get("open_applications", False)
        self.active_war: bool = kwargs.get("active_war", False)
        self.disband_condition: Optional[str] = kwargs.get("disband_condition")
        self.disband_date = try_datetime(kwargs.get("disband_date"))
        self.homepage: Optional[str] = kwargs.get("homepage")
        self.members: List[GuildMember] = kwargs.get("members", [])
        self.invites: List[GuildInvite] = kwargs.get("invites", [])

    def __repr__(self):
        return "<{0.__class__.__name__} name={0.name!r} world={0.world!r}>".format(self)

    # region Properties
    @property
    def member_count(self):
        """:class:`int`: The number of members in the guild."""
        return len(self.members)

    @property
    def online_count(self):
        """:class:`int`: The number of online members in the guild."""
        return len(self.online_members)

    @property
    def online_members(self):
        """:class:`list` of :class:`GuildMember`: List of currently online members."""
        return list(filter(lambda m: m.online, self.members))

    @property
    def ranks(self) -> List[str]:
        """:class:`list` of :class:`str`: Ranks in their hierarchical order."""
        return list(OrderedDict.fromkeys((m.rank for m in self.members)))

    @property
    def members_by_rank(self) -> Dict[str, List['GuildMember']]:
        """:class:`dict`: Gets a mapping of members, grouped by their guild rank."""
        rank_dict = defaultdict(list)
        [rank_dict[m.rank].append(m) for m in self.members]
        return dict(rank_dict)
    # endregion

    # region Public methods
    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the HTML content of the guild's page.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`Guild`
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
            name_header = parsed_content.find('h1')
            guild = Guild(name_header.text.strip())
        except AttributeError:
            raise InvalidContent("content does not belong to a Tibia.com guild page.")

        if not guild._parse_logo(parsed_content):
            raise InvalidContent("content does not belong to a Tibia.com guild page.")

        info_container = parsed_content.find("div", id="GuildInformationContainer")
        guild._parse_guild_info(info_container)
        guild._parse_application_info(info_container)
        guild._parse_guild_homepage(info_container)
        guild._parse_guild_guildhall(info_container)
        guild._parse_guild_disband_info(info_container)
        guild._parse_guild_members(parsed_content)

        if guild.guildhall and guild.members:
            guild.guildhall.owner = guild.members[0].name

        return guild

    # endregion

    # region Private methods
    def _parse_current_member(self, previous_rank, values):
        """
        Parses the column texts of a member row into a member dictionary.

        Parameters
        ----------
        previous_rank: :class:`dict`[int, str]
            The last rank present in the rows.
        values: tuple[:class:`str`]
            A list of row contents.
        """
        rank, name, vocation, level, joined, status = values
        rank = previous_rank[1] if rank == " " else rank
        title = None
        previous_rank[1] = rank
        m = title_regex.match(name)
        if m:
            name = m.group(1)
            title = m.group(2)
        self.members.append(GuildMember(name, rank, title, int(level), vocation, joined=joined,
                                        online=status == "online"))

    def _parse_application_info(self, info_container):
        """
        Parses the guild's application info.

        Parameters
        ----------
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        m = applications_regex.search(info_container.text)
        if m:
            self.open_applications = m.group(1) == "opened"
        self.active_war = "during war" in info_container.text

    def _parse_guild_disband_info(self, info_container):
        """
        Parses the guild's disband info, if available.

        Parameters
        ----------
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        m = disband_regex.search(info_container.text)
        if m:
            self.disband_condition = m.group(2)
            self.disband_date = parse_tibia_date(m.group(1).replace("\xa0", " "))

    def _parse_guild_guildhall(self, info_container):
        """
        Parses the guild's guildhall info.

        Parameters
        ----------
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        m = guildhall_regex.search(info_container.text)
        if m:
            paid_until = parse_tibia_date(m.group("date").replace("\xa0", " "))
            self.guildhall = GuildHouse(m.group("name"), self.world, paid_until_date=paid_until)

    def _parse_guild_homepage(self, info_container):
        """
        Parses the guild's homepage info.

        Parameters
        ----------
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        m = homepage_regex.search(info_container.text)
        if m:
            self.homepage = m.group(1)

    def _parse_guild_info(self, info_container):
        """
        Parses the guild's general information and applies the found values.

        Parameters
        ----------
        info_container: :class:`bs4.Tag`
            The parsed content of the information container.
        """
        m = founded_regex.search(info_container.text)
        if m:
            description = m.group("desc").strip()
            self.description = description if description else None
            self.world = m.group("world")
            self.founded = parse_tibia_date(m.group("date").replace("\xa0", " "))
            self.active = "currently active" in m.group("status")

    def _parse_logo(self, parsed_content):
        """
        Parses the guild logo and saves it to the instance.

        Parameters
        ----------
        parsed_content: :class:`bs4.Tag`
            The parsed content of the page.

        Returns
        -------
        :class:`bool`
            Whether the logo was found or not.
        """
        logo_img = parsed_content.find('img', {'height': '64'})
        if logo_img is None:
            return False

        self.logo_url = logo_img["src"]
        return True

    def _parse_guild_members(self, parsed_content):
        """
        Parses the guild's member and invited list.

        Parameters
        ----------
        parsed_content: :class:`bs4.Tag`
            The parsed content of the guild's page
        """
        member_rows = parsed_content.find_all("tr", {'bgcolor': ["#D4C0A1", "#F1E0C6"]})
        previous_rank = {}
        for row in member_rows:
            columns = row.find_all('td')
            values = tuple(c.text.replace("\u00a0", " ") for c in columns)
            if len(columns) == COLS_GUILD_MEMBER:
                self._parse_current_member(previous_rank, values)
            if len(columns) == COLS_INVITED_MEMBER:
                self._parse_invited_member(values)

    def _parse_invited_member(self, values):
        """
        Parses the column texts of an invited row into a invited dictionary.

        Parameters
        ----------
        values: tuple[:class:`str`]
            A list of row contents.
        """
        name, date = values
        if date != "Invitation Date":
            self.invites.append(GuildInvite(name, date))
    # endregion


class GuildMember(abc.BaseCharacter, abc.Serializable):
    """
    Represents a guild member.

    Attributes
    --------------
    rank: :class:`str`
        The rank the member belongs to
    name: :class:`str`
        The name of the guild member.
    title: :class:`str`, optional
        The member's title.
    level: :class:`int`
        The member's level.
    vocation: :class:`Vocation`
        The member's vocation.
    joined: :class:`datetime.date`
        The day the member joined the guild.
    online: :class:`bool`
        Whether the member is online or not.
    """
    __slots__ = ("name", "rank", "title", "level", "vocation", "joined", "online")

    def __init__(self, name=None, rank=None, title=None, level=0, vocation=None, **kwargs):
        self.name: str = name
        self.rank: str = rank
        self.title: Optional[str] = title
        self.vocation = try_enum(Vocation, vocation)
        self.level = int(level)
        self.online: bool = kwargs.get("online", False)
        self.joined = try_date(kwargs.get("joined"))


class GuildInvite(abc.BaseCharacter, abc.Serializable):
    """Represents an invited character

    Attributes
    ------------
    name: :class:`str`
        The name of the character

    date: :class:`datetime.date`
        The day when the character was invited.
    """
    __slots__ = (
        "name",
        "date",
    )

    def __init__(self, name=None, date=None):
        self.name: str = name
        self.date = try_date(date)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} date={self.date!r}>"


class GuildWars(abc.Serializable):
    """Represents a guild's wars.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    name: :class:`str`
        The name of the guild.
    current: :class:`GuildWarEntry`
        The current war the guild is involved in.
    history: :class:`list` of :class:`GuildWarEntry`
        The previous wars the guild has been involved in."""

    __slots__ = (
        'name',
        'current',
        'history',
    )

    def __init__(self, name, current=None, history=None):
        self.name: str = name
        self.current: Optional[GuildWarEntry] = current
        self.history: List[GuildWarEntry] = history or []

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r}>"

    @property
    def url(self):
        """:class:`str`: The URL of this guild's war page on Tibia.com."""
        return self.get_url(self.name)

    @classmethod
    def get_url(cls, name):
        """
        Gets the URL to the guild's war page of a guild with the given name.

        Parameters
        ----------
        name: class:`str`
            The name of the guild.

        Returns
        -------
        :class:`str`
            The URL to the guild's war page.
        """
        return Guild.get_url_wars(name)

    @classmethod
    def from_content(cls, content):
        """Gets a guild's war information from Tibia.com's content

        Parameters
        ----------
        content: :class:`str`
            The HTML content of a guild's war section in Tibia.com

        Returns
        -------
        :class:`GuildWars`
            The guild's war information.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            table_current, table_history = parsed_content.find_all("div", attrs={"class": "TableContainer"})
            current_table_content = table_current.find("table", attrs={"class": "TableContent"})
            current_war = None
            guild_name = None
            if current_table_content is not None:
                for br in current_table_content.find_all("br"):
                    br.replace_with("\n")
                current_war = cls._parse_current_war_information(current_table_content.text)
            else:
                current_war_text = table_current.text
                current_war_match = war_current_empty.search(current_war_text)
                guild_name = current_war_match.group(1)

            history_entries = []
            history_contents = table_history.find_all("table", attrs={"class": "TableContent"})
            for history_content in history_contents:
                for br in history_content.find_all("br"):
                    br.replace_with("\n")
                entry = cls._parse_war_history_entry(history_content.text)
                history_entries.append(entry)

            if current_war:
                guild_name = current_war.guild_name
            elif history_entries:
                guild_name = history_entries[0].guild_name

            return cls(guild_name, current=current_war, history=history_entries)
        except ValueError as e:
            raise InvalidContent("content does not belong to the guild wars section", e)

    @classmethod
    def _parse_current_war_information(cls, text):
        """Parses the guild's current war information.

        Parameters
        ----------
        text: :class:`str`
            The text describing the current war's information.

        Returns
        -------
        :class:`GuildWarEntry`
            The guild's war entry for the current war.
        """
        text = text.replace('\xa0', ' ').strip()
        names_match = war_guilds_regegx.search(text)
        guild_name, opposing_name = names_match.groups()
        scores_match = war_score_regex.findall(text)
        guild_score, opposing_score = scores_match
        fee_match = war_fee_regex.findall(text)
        guild_fee, opposing_fee = fee_match

        score_limit_match = war_score_limit_regex.search(text)
        score_limit = score_limit_match.group(1)

        end_date_match = war_end_regex.search(text)
        end_date_str = end_date_match.group(1)
        end_date = parse_tibia_date(end_date_str)

        entry = GuildWarEntry(guild_name=guild_name, opponent_name=opposing_name, guild_score=int(guild_score),
                              opponent_score=int(opposing_score), guild_fee=int(guild_fee),
                              opponent_fee=int(opposing_fee), score_limit=int(score_limit), end_date=end_date)
        return entry

    @classmethod
    def _parse_war_history_entry(cls, text):
        """Parses a guild's war information.

        Parameters
        ----------
        text: :class:`str`
            The text describing the war's information.

        Returns
        -------
        :class:`GuildWarEntry`
            The guild's war entry described in the text..
        """
        text = text.replace('\xa0', ' ').strip()
        header_match = war_history_header_regex.search(text)
        guild_name, opposing_name = header_match.groups()
        if "disbanded guild" in opposing_name:
            opposing_name = None
        start_duration_match = war_start_duration_regex.search(text)
        start_str, duration_str = start_duration_match.groups()
        start_date = parse_tibia_date(start_str)
        duration = datetime.timedelta(days=int(duration_str))
        kills_match = kills_needed_regex.search(text)
        kills_needed = int(kills_match.group(1))
        fee_match = war_history_fee_regex.search(text)
        guild_fee, opponent_fee = fee_match.groups()
        winner = None
        surrender = False
        end_date = None
        guild_score = opponent_score = 0
        surrender_match = surrender_regex.search(text)
        if surrender_match:
            surrending_guild = surrender_match.group(1)
            end_date = parse_tibia_date(surrender_match.group(2))
            winner = guild_name if surrending_guild != guild_name else opposing_name
            surrender = True

        war_score_match = war_score_regex.findall(text)
        if war_score_match and len(war_score_match) == 2:
            guild_score, opponent_score = war_score_match
            guild_score = int(guild_score)
            opponent_score = int(guild_score)

        war_end_match = war_ended_regex.search(text)
        if war_end_match:
            end_date = parse_tibia_date(war_end_match.group(1))
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

        entry = GuildWarEntry(guild_name=guild_name, opponent_name=opposing_name, start_date=start_date,
                              duration=duration, score_limit=kills_needed, guild_fee=int(guild_fee),
                              opponent_fee=int(opponent_fee), surrender=surrender, winner=winner, end_date=end_date,
                              opponent_score=opponent_score, guild_score=guild_score)
        return entry


class GuildWarEntry(abc.Serializable):
    """Represents a guild war entry.

    .. versionadded:: 3.0.0

    Attributes
    ----------
    guild_name: :class:`str`
        The name of the guild.
    guild_score: :class:`int`
        The number of kills the guild has scored.
    guild_fee: :class:`int`
        The number of gold coins the guild will pay if they lose the war.
    opponent_name: :class:`str`
        The name of the opposing guild. If the guild no longer exist, this will be :obj:`None`.
    opponent_score: :class:`int`
        The number of kills the opposing guild has scored.
    opponent_fee: :class:`int`
        The number of gold coins the opposing guild will pay if they lose the war.
    start_date: :class:`datetime.date`
        The date when the war started.

        When a war is in progress, the start date is not visible.
    score_limit: :class:`int`
        The number of kills needed to win the war.
    duration: :class:`datetime.timedelta`
        The set duration of the war.

        When a war is in progress, the duration is not visible.
    end_date: :class:`datetime.date`
        The deadline for the war to finish if the score is not reached for wars in progress, or the date when the
        war ended.
    winner: :class:`str`
        The name of the guild that won.

        Note that if the winning guild is disbanded, this may be :obj:`None`.
    surrender: :class:`bool`
        Whether the losing guild surrendered or not.
    """
    __slots__ = (
        "guild_name",
        "guild_score",
        "guild_fee",
        "opponent_name",
        "opponent_score",
        "opponent_fee",
        "start_date",
        "score_limit",
        "duration",
        "end_date",
        "winner",
        "surrender",
    )

    def __init__(self, **kwargs):
        self.guild_name = kwargs.get("guild_name")
        self.guild_score = kwargs.get("guild_score", 0)
        self.guild_fee = kwargs.get("guild_fee", 0)
        self.opponent_name = kwargs.get("opponent_name")
        self.opponent_score = kwargs.get("opponent_score", 0)
        self.opponent_fee = kwargs.get("opponent_fee", 0)
        self.start_date = kwargs.get("start_date")
        self.score_limit = kwargs.get("score_limit", 0)
        self.duration = kwargs.get("duration")
        self.end_date = kwargs.get("end_date")
        self.winner = kwargs.get("winner")
        self.surrender = kwargs.get("surrender", False)

    def __repr__(self):
        return "<{0.__class__.__name__} guild_name={0.guild_name!r} opponent_name={0.opponent_name!r}>".format(self)

    @property
    def guild_url(self):
        """:class:`str`: The URL to the guild's information page on Tibia.com."""
        return Guild.get_url(self.guild_name)

    @property
    def opponent_guild_url(self):
        """:class:`str`: The URL to the opposing guild's information page on Tibia.com."""
        return Guild.get_url(self.opponent_name) if self.opponent_name else None


class ListedGuild(abc.BaseGuild, abc.Serializable):
    """
    Represents a Tibia guild in the guild list of a world.

    Attributes
    ------------
    name: :class:`str`
        The name of the guild.
    logo_url: :class:`str`
        The URL to the guild's logo.
    description: :class:`str`, optional
        The description of the guild.
    world: :class:`str`
        The world this guild belongs to.
    active: :class:`bool`
        Whether the guild is active or still in formation.
    """
    __slots__ = (
        "name",
        "logo_url",
        "description",
        "world",
        "active",
    )

    def __init__(self, name, world, logo_url=None, description=None, active=False):
        self.name: str = name
        self.world: str = world
        self.logo_url: str = logo_url
        self.description: Optional[str] = description
        self.active: bool = active

    # region Public methods
    @classmethod
    def list_from_content(cls, content):
        """
        Gets a list of guilds from the HTML content of the world guilds' page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`list` of :class:`ListedGuild`
            List of guilds in the current world. :obj:`None` if it's the list of a world that doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a guild's page.
        """
        parsed_content = parse_tibiacom_content(content)
        selected_world = parsed_content.find('option', selected=True)
        try:
            if "choose world" in selected_world.text:
                # It belongs to a world that doesn't exist
                return None
            world = selected_world.text
        except AttributeError:
            raise InvalidContent("Content does not belong to world guild list.")
        # First TableContainer contains world selector.
        _, *containers = parsed_content.find_all('div', class_="TableContainer")
        guilds = []
        for container in containers:
            header = container.find('div', class_="Text")
            active = "Active" in header.text
            header, *rows = container.find_all("tr", {'bgcolor': ["#D4C0A1", "#F1E0C6"]})
            for row in rows:
                columns = row.find_all('td')
                logo_img = columns[0].find('img')["src"]
                description_lines = columns[1].get_text("\n").split("\n", 1)
                name = description_lines[0]
                description = None
                if len(description_lines) > 1:
                    description = description_lines[1].replace("\r", "").replace("\n", " ")
                guild = cls(name, world, logo_img, description, active)
                guilds.append(guild)
        return guilds

    # endregion
