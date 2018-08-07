import tibiapy

class Guild:
    """
    Represents a Tibia guild.

    Attributes
    ------------
    name: :class:`str`
        The name of the guild
    description: Optional[:class:`str`]
        The description of the guild.
    guildhall: :class:`dict`
        The guild's guildhall.
    open_applications: :class:`bool`
        Whether applications are open or not.
    homepage: :class:`str`
        The guild's homepage
    founded: :class:`str`
        The date the guild was founded.
    guild_logo: :class:`str`
        The URL to the guild's logo.
    members: :class:`list`
        List of guild members.
    """
    pass


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
