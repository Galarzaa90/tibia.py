import json
import re

from bs4 import BeautifulSoup, SoupStrainer

import tibiapy

founded_regex = re.compile(r'(?P<desc>.*)The guild was founded on (?P<world>\w+) on (?P<date>[^.]+)\.\nIt is (?P<status>[^.]+).',
                           re.DOTALL)
applications_regex = re.compile(r'Guild is (\w+) for applications\.')
homepage_regex = re.compile(r'The official homepage is at ([\w.]+)\.')
guildhall_regex = re.compile(r'Their home on \w+ is (?P<name>[^.]+). The rent is paid until (?P<date>[^.]+)')
disband_regex = re.compile(r'It will be disbanded on (\w+\s\d+\s\d+)\s([^.]+).')


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
    founded: :class:`str`
        The date the guild was founded.
    active: :class:`bool`
        Whether the guild is active or still in formation.
    guildhall: :class:`dict`
        The guild's guildhall.
    open_applications: :class:`bool`
        Whether applications are open or not.
    disband_condition: Optional[:class:`str`]
        The reason why the guild will get disbanded.
    disband_date: Optional[:class:`str`]
        The date when the guild will be disbanded if the condition hasn't been meet.
    homepage: :class:`str`
        The guild's homepage
    members: :class:`list`
        List of guild members.
    invites: :class:`list`
        List of invited characters.
    """
    __slots__ = ("name", "logo_url", "description", "world", "founded", "active", "guildhall", "open_applications",
                 "disband_condition", "disband_date", "homepage", "members", "invites")

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
            guild["description"] =  description if description else None
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
                guild["members"].append({
                    "rank": rank,
                    "name": name,
                    "vocation": vocation,
                    "level": int(level),
                    "joined": joined,
                    "online": status == "online"
                })
            # Invited character
            if len(columns) == 2:
                name, invite = values
                guild["invites"].append({
                    "name": name,
                    "invite": invite
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
            The character contained in the page.
        """
        _guild = Guild._parse(content)

        guild = Guild()
        guild.name = _guild["name"]
        guild.description = _guild["description"]
        guild.logo_url = _guild["logo_url"]
        guild.world = _guild["world"]
        guild.founded = _guild["founded"]
        guild.active = _guild["active"]
        guild.guildhall = _guild["guildhall"]
        guild.open_applications = _guild["open_applications"]
        guild.disband_condition = _guild["disband_condition"]
        guild.disband_date = _guild["disband_date"]
        guild.homepage = _guild["homepage"]
        guild.members = _guild["members"]
        guild.invites = _guild["invites"]
        return guild


class GuildMember(tibiapy.abc.Character):
    """
    Represents a guild member.

    Attributes
    --------------
    rank: :class:`str`
        The rank the member belongs to

    name: :class:`str`
        The name of the guild member.

    nick: Optional[:class:`str`]
        The member's nick.

    level: :class:`int`
        The member's level.

    vocation: :class:`str`
        The member's vocation.

    joined: :class:`str`
        The day the member joined the guild.

    online: :class:`bool`
        Whether the meber is online or not.
    """
    pass
