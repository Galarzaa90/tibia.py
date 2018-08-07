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
    """

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
            guild["founded_date"] = m.group("date").replace("\xa0", " ")
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
