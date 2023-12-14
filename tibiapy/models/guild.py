"""Models for guilds and members."""
import datetime
from collections import defaultdict
from typing import Optional, List, Dict, OrderedDict

from pydantic import computed_field

from tibiapy.enums import Vocation
from tibiapy.models import BaseCharacter, BaseHouse, BaseGuild, BaseModel
from tibiapy.urls import get_world_guilds_url, get_guild_url, get_guild_wars_url

__all__ = (
    "GuildHouse",
    "GuildMember",
    "GuildInvite",
    "Guild",
    "GuildEntry",
    "GuildsSection",
    "GuildWarEntry",
    "GuildWars",
)

from tibiapy.utils import take_while


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
    joined_on: datetime.date
    """The day the member joined the guild."""
    is_online: bool
    """Whether the member is online or not."""


class GuildInvite(BaseCharacter):
    """Represents an invited character."""

    invited_on: datetime.date
    """The day when the character was invited."""


class GuildHouse(BaseHouse):
    """A guildhall owned by a guild.

    By limitation of Tibia.com, the ID of the guildhall is not available.
    """

    paid_until: datetime.date
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
    disband_date: Optional[datetime.date] = None
    """The date when the guild will be disbanded if the condition hasn't been meet."""
    disband_condition: Optional[str] = None
    """The reason why the guild will get disbanded."""
    homepage: Optional[str] = None
    """The guild's homepage, if any."""
    members: List[GuildMember]
    """List of guild members."""
    invites: List[GuildInvite]
    """List of invited characters."""

    @computed_field
    @property
    def member_count(self) -> int:
        """The number of members in the guild."""
        return len(self.members)

    @computed_field
    @property
    def online_count(self) -> int:
        """The number of online members in the guild."""
        return len(self.online_members)

    @property
    def online_members(self) -> List[GuildMember]:
        """List of currently online members."""
        return list(filter(lambda m: m.is_online, self.members))

    @computed_field
    @property
    def ranks(self) -> List[str]:
        """Ranks in their hierarchical order."""
        return list(OrderedDict.fromkeys(m.rank for m in self.members))

    @property
    def leader(self) -> GuildMember:
        """Get the leader of the guild."""
        return self.members[0]

    @property
    def vice_leaders(self) -> List[GuildMember]:
        """The vice leader of the guilds."""
        if len(self.members) <= 1:
            return []

        return list(take_while(self.members[1:], lambda m: m.rank == self.members[1].rank))

    @property
    def members_by_rank(self) -> Dict[str, List[GuildMember]]:
        """Get a mapping of members, grouped by their guild rank."""
        rank_dict = defaultdict(list)
        [rank_dict[m.rank].append(m) for m in self.members]
        return dict(rank_dict)


class GuildEntry(BaseGuild):
    """Represents a Tibia guild in the guild list of a world."""

    logo_url: str
    """The URL to the guild's logo."""
    description: Optional[str] = None
    """The description of the guild."""
    world: str
    """The world this guild belongs to."""
    active: bool
    """Whether the guild is active or still in formation."""


class GuildsSection(BaseModel):
    """The guilds section in Tibia.com."""

    world: Optional[str] = None
    """The name of the world. If :obj:`None`, the section belongs to a world that doesn't exist."""
    entries: List[GuildEntry] = []
    """The list of guilds in the world."""
    available_worlds: List[str]
    """The list of worlds available for selection."""

    @property
    def active_guilds(self) -> List[GuildEntry]:
        """Get a list of the guilds that are active."""
        return [g for g in self.entries if g.active]

    @property
    def in_formation_guilds(self) -> List[GuildEntry]:
        """Get a list of the guilds that are in course of formation."""
        return [g for g in self.entries if not g.active]

    @property
    def url(self) -> str:
        """Get the URL to this guild section."""
        return get_world_guilds_url(self.world)


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
    def guild_url(self) -> str:
        """The URL to the guild's information page on Tibia.com."""
        return get_guild_url(self.guild_name)

    @property
    def opponent_guild_url(self) -> Optional[str]:
        """The URL to the opposing guild's information page on Tibia.com."""
        return get_guild_url(self.opponent_name) if self.opponent_name else None


class GuildWars(BaseModel):
    """Represents a guild's wars."""

    name: Optional[str] = None
    """The name of the guild."""
    is_current: Optional[GuildWarEntry] = None
    """The current war the guild is involved in."""
    history: List[GuildWarEntry]
    """The previous wars the guild has been involved in."""

    @property
    def url(self) -> str:
        """The URL of this guild's war page on Tibia.com."""
        return get_guild_wars_url(self.name)
