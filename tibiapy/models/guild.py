import datetime
from collections import defaultdict
from typing import Optional, List, Dict, OrderedDict

from pydantic import BaseModel

from tibiapy import Vocation
from tibiapy.models.base import BaseCharacter, BaseHouse, BaseGuild
from tibiapy.utils import get_tibia_url


__all__ = (
    'GuildHouse',
    'GuildMember',
    'GuildInvite',
    'Guild',
    'GuildEntry',
    'GuildsSection',
    'GuildWarEntry',
    'GuildWars'
)


class GuildMember(BaseCharacter):
    """Represents a guild member."""

    rank: str
    """The rank the member belongs to"""
    title: Optional[str] = None
    """The member's title."""
    level: int
    """The member's level."""
    vocation: Vocation
    """The member's vocation."""
    joined: datetime.date
    """The day the member joined the guild."""
    online: bool
    """Whether the member is online or not."""


class GuildInvite(BaseCharacter):
    """Represents an invited character."""
    date: datetime.date
    """The day when the character was invited."""


class GuildHouse(BaseHouse):
    """A guildhall owned by a guild.

    By limitation of Tibia.com, the ID of the guildhall is not available."""

    paid_until_date: datetime.date
    """The date the last paid rent is due."""


class Guild(BaseGuild):
    """A Tibia guild, viewed from its guild's page."""

    logo_url: str
    """The URL to the guild's logo."""
    description: Optional[str] = None
    """The description of the guild."""
    world: str
    """The world this guild belongs to."""
    founded: datetime.date
    """The day the guild was founded."""
    active: bool
    """Whether the guild is active or still in formation."""
    guildhall: Optional[GuildHouse] = None
    """The guild's guildhall if any."""
    open_applications: bool = False
    """Whether applications are open or not."""
    active_war: bool
    """Whether the guild is currently in an active war or not."""
    disband_date: Optional[datetime.datetime]
    """The date when the guild will be disbanded if the condition hasn't been meet."""
    disband_condition: Optional[str]
    """The reason why the guild will get disbanded."""
    homepage: Optional[str]
    """The guild's homepage, if any."""
    members: List[GuildMember]
    """List of guild members."""
    invites: List[GuildInvite]
    """List of invited characters."""

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
        """:class:`dict`: Get a mapping of members, grouped by their guild rank."""
        rank_dict = defaultdict(list)
        [rank_dict[m.rank].append(m) for m in self.members]
        return dict(rank_dict)


class GuildEntry(BaseGuild):
    """Represents a Tibia guild in the guild list of a world."""

    logo_url: str
    """The URL to the guild's logo."""
    description: Optional[str]
    """The description of the guild."""
    world: str
    """The world this guild belongs to."""
    active: bool
    """Whether the guild is active or still in formation."""


class GuildsSection(BaseModel):
    world: Optional[str] = None
    """The name of the world. If :obj:`None`, the section belongs to a world that doesn't exist."""
    entries: List[GuildEntry] = []
    """The list of guilds in the world."""
    available_worlds: List[str]
    """The list of worlds available for selection."""

    @property
    def active_guilds(self):
        """:class:`list` of :class:`GuildEntry`: Get a list of the guilds that are active."""
        return [g for g in self.entries if g.active]

    @property
    def in_formation_guilds(self):
        """:class:`list` of :class:`GuildEntry`: Get a list of the guilds that are in course of formation."""
        return [g for g in self.entries if not g.active]

    @property
    def url(self):
        """:class:`str`: Get the URL to this guild section."""
        return self.get_url(self.world)

    @classmethod
    def get_url(cls, world):
        """Get the Tibia.com URL for the guild section of a specific world.

        Parameters
        ----------
        world: :class:`str`
            The name of the world.

        Returns
        -------
        :class:`str`
            The URL to the guild's page
        """
        return get_tibia_url("community", "guilds", world=world)


class GuildWarEntry(BaseModel):
    """Represents a guild war entry."""

    guild_name: str
    """The name of the guild."""
    guild_score: int
    """The number of kills the guild has scored."""
    guild_fee: int
    """The number of gold coins the guild will pay if they lose the war."""
    opponent_name: Optional[str] = None
    """The name of the opposing guild. If the guild no longer exist, this will be :obj:`None`."""
    opponent_score: int
    """The number of kills the opposing guild has scored."""
    opponent_fee: int
    """The number of gold coins the opposing guild will pay if they lose the war."""
    start_date: Optional[datetime.date] = None
    """The date when the war started.

    When a war is in progress, the start date is not visible."""
    score_limit: int
    """The number of kills needed to win the war."""
    duration: Optional[datetime.timedelta] = None
    """The set duration of the war.

    When a war is in progress, the duration is not visible."""
    end_date: Optional[datetime.date] = None
    """The deadline for the war to finish if the score is not reached for wars in progress, or the date when the
     war ended."""
    winner: Optional[str] = None
    """The name of the guild that won.

    Note that if the winning guild is disbanded, this may be :obj:`None`."""
    surrender: bool
    """Whether the losing guild surrendered or not."""

    @property
    def guild_url(self):
        """:class:`str`: The URL to the guild's information page on Tibia.com."""
        return Guild.get_url(self.guild_name)

    @property
    def opponent_guild_url(self):
        """:class:`str`: The URL to the opposing guild's information page on Tibia.com."""
        return Guild.get_url(self.opponent_name) if self.opponent_name else None


class GuildWars(BaseModel):
    """Represents a guild's wars."""

    name: Optional[str] = None
    """The name of the guild."""
    current: Optional[GuildWarEntry] = None
    """The current war the guild is involved in."""
    history: List[GuildWarEntry]
    """The previous wars the guild has been involved in."""

    @property
    def url(self):
        """:class:`str`: The URL of this guild's war page on Tibia.com."""
        return self.get_url(self.name)

    @classmethod
    def get_url(cls, name):
        """Get the URL to the guild's war page of a guild with the given name.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild.

        Returns
        -------
        :class:`str`
            The URL to the guild's war page.
        """
        return Guild.get_url_wars(name)


