import json
import re
import urllib.parse

from bs4 import BeautifulSoup, SoupStrainer

from . import abc
from .utils import parse_tibia_date
from .const import GUILD_URL

founded_regex = re.compile(r'(?P<desc>.*)The guild was founded on (?P<world>\w+) on (?P<date>[^.]+)\.\nIt is (?P<status>[^.]+).',
                           re.DOTALL)
applications_regex = re.compile(r'Guild is (\w+) for applications\.')
homepage_regex = re.compile(r'The official homepage is at ([\w.]+)\.')
guildhall_regex = re.compile(r'Their home on \w+ is (?P<name>[^.]+). The rent is paid until (?P<date>[^.]+)')
disband_regex = re.compile(r'It will be disbanded on (\w+\s\d+\s\d+)\s([^.]+).')
title_regex = re.compile(r'([\w\s]+)\s\(([^)]+)\)')


class Guild:
    """
    Represents a Tibia guild.

    Attributes
    ------------
    name: :class:`str`
        The name of the guild. Names are case sensitive.
    logo_url: :class:`str`
        The URL to the guild's logo.
    description: Optional[:class:`str`]
        The description of the guild.
    world: :class:`str`
        The world where this guild is in.
    founded: :class:`datetime.date`
        The day the guild was founded.
    active: :class:`bool`
        Whether the guild is active or still in formation.
    guildhall: Optional[:class:`dict`]
        The guild's guildhall.
    open_applications: :class:`bool`
        Whether applications are open or not.
    disband_condition: Optional[:class:`str`]
        The reason why the guild will get disbanded.
    disband_date: Optional[:class:`str`]
        The date when the guild will be disbanded if the condition hasn't been meet.
    homepage: :class:`str`
        The guild's homepage
    members: List[:class:`GuildMember`]
        List of guild members.
    invites: List[:class:`GuildInvite`]
        List of invited characters.
    """
    __slots__ = ("name", "logo_url", "description", "world", "founded", "active", "guildhall", "open_applications",
                 "disband_condition", "disband_date", "homepage", "members", "invites")

    def __init__(self, ** kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def member_count(self):
        """:class:`int`: The number of members in the guild."""
        return len(self.members)

    @property
    def ranks(self):
        """List[:class:`str`]: Ranks in their hierarchical order."""
        return list({m["rank"] for m in self.members})

    @property
    def online_members(self):
        """List[:class:`GuildMember`]: List of currently online members."""
        return list(filter(lambda m: m.online, self.members))

    @property
    def url(self):
        """:class:`str`: The URL to the guild's information page."""
        return GUILD_URL + urllib.parse.quote(self.name.encode('iso-8859-1'))

    @staticmethod
    def _parse(content):
        if "An internal error has occurred" in content:
            return None
        guild = {}
        parsed_content = BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), 'lxml',
                                       parse_only=SoupStrainer("div", class_="BoxContent"))

        logo = parsed_content.find('img', {'height': '64'})
        header = parsed_content.find('h1')
        guild["name"] = header.text
        guild["logo_url"] = logo["src"]
        info_container = parsed_content.find("div", id="GuildInformationContainer")
        m = founded_regex.search(info_container.text)
        if m:
            description = m.group("desc").strip()
            guild["description"] = description if description else None
            guild["world"] = m.group("world")
            guild["founded"] = m.group("date").replace("\xa0", " ")
            guild["active"] = "currently active" in m.group("status")

        m = applications_regex.search(info_container.text)
        if m:
            guild["open_applications"] = m.group(1) == "opened"

        m = homepage_regex.search(info_container.text)
        if m:
            guild["homepage"] = m.group(1)
        else:
            guild["homepage"] = None

        m = guildhall_regex.search(info_container.text)
        if m:
            guild["guildhall"] = {"name": m.group("name"), "paid_until": m.group("date").replace("\xa0", " ")}
        else:
            guild["guildhall"] = None

        m = disband_regex.search(info_container.text)
        if m:
            guild["disband_condition"] = m.group(2)
            guild["disband_date"] = m.group(1).replace("\xa0", " ")
        else:
            guild["disband_condition"] = None
            guild["disband_date"] = None

        member_rows = parsed_content.find_all("tr", {'bgcolor': ["#D4C0A1", "#F1E0C6"]})
        guild["members"] = []
        guild["invites"] = []
        previous_rank = ""
        for row in member_rows:
            columns = row.find_all('td')
            values = (c.text.replace("\u00a0", " ") for c in columns)
            # Current member
            if len(columns) == 6:
                rank, name, vocation, level, joined, status = values
                rank = previous_rank if rank == " " else rank
                previous_rank = rank
                m = title_regex.match(name)
                if m:
                    name = m.group(1)
                    title = m.group(2)
                else:
                    title = None
                guild["members"].append({
                    "rank": rank,
                    "name": name,
                    "title": title,
                    "vocation": vocation,
                    "level": int(level),
                    "joined": joined,
                    "online": status == "online"
                })
            # Invited character
            if len(columns) == 2:
                name, date = values
                if date == "Invitation Date":
                    continue
                guild["invites"].append({
                    "name": name,
                    "date": date
                })

        return guild

    @staticmethod
    def parse_to_json(content, indent=None):
        """Static method that creates a JSON string from the html content of the guild's page.

        Parameters
        -------------
        content: str
            The HTML content of the page.
        indent: int
            The number of spaces to indent the output with.

        Returns
        ------------
        :class:`str`
            A string in JSON format."""
        char_dict = Guild._parse(content)
        return json.dumps(char_dict, indent=indent)

    @staticmethod
    def from_content(content):
        """Creates an instance of the class from the html content of the guild's page.


        Parameters
        -----------
        content: str
            The HTML content of the page.

        Returns
        ----------
        :class:`Guild`
            The guild contained in the page.
        """
        _guild = Guild._parse(content)

        guild = Guild()
        guild.name = _guild["name"]
        guild.description = _guild["description"]
        guild.logo_url = _guild["logo_url"]
        guild.world = _guild["world"]
        guild.founded = parse_tibia_date(_guild["founded"])
        guild.active = _guild["active"]
        guild.guildhall = _guild["guildhall"]
        guild.open_applications = _guild["open_applications"]
        guild.disband_condition = _guild["disband_condition"]
        guild.disband_date = _guild["disband_date"]
        guild.homepage = _guild["homepage"]
        guild.members = []
        for member in _guild["members"]:
            guild.members.append(GuildMember(rank=member["rank"], name=member["name"], level=member["level"],
                                             vocation=member["vocation"], title=member["title"],
                                             online=member["online"], joined=parse_tibia_date(member["joined"])))

        guild.invites = []
        for invite in _guild["invites"]:
            guild.invites.append(GuildInvite(name=invite["name"], date=parse_tibia_date(invite["date"])))
        return guild


class GuildMember(abc.Character):
    """
    Represents a guild member.

    Attributes
    --------------
    rank: :class:`str`
        The rank the member belongs to

    name: :class:`str`
        The name of the guild member.

    title: Optional[:class:`str`]
        The member's title.

    level: :class:`int`
        The member's level.

    vocation: :class:`str`
        The member's vocation.

    joined: :class:`datetime.date`
        The day the member joined the guild.

    online: :class:`bool`
        Whether the member is online or not.
    """
    __slots__ = ("name", "rank", "title", "level", "vocation", "joined", "online")

    def __init__(self, ** kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class GuildInvite(abc.Character):
    """Represents an invited character

    Attributes
    ------------
    name: :class:`str`
        The name of the character

    date: :class:`datetime.date`
        The day when the character was invited."""

    __slots__ = ("date", )

    def __init__(self, ** kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)