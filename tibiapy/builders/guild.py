from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from tibiapy.models import GuildEntry, Guild, GuildWars, GuildWarEntry

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from tibiapy.models import GuildHouse, GuildMember, GuildInvite


class _BaseGuildBuilder:

    def __init__(self):
        self._name = None
        self._logo_url = None
        self._description = None

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def logo_url(self, logo_url: str) -> Self:
        self._logo_url = logo_url
        return self

    def description(self, description: Optional[str]) -> Self:
        self._description = description
        return self

    def build(self):
        raise NotImplementedError


class GuildEntryBuilder(_BaseGuildBuilder):

    def __init__(self):
        super().__init__()
        self._world = None
        self._active = None

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def active(self, active: bool) -> Self:
        self._active = active
        return self

    def build(self) -> GuildEntry:
        return GuildEntry(
            name=self._name,
            logo_url=self._logo_url,
            description=self._description,
            world=self._world,
            active=self._active,
        )


class GuildBuilder(_BaseGuildBuilder):

    def __init__(self):
        super().__init__()
        self._logo_url = None
        self._description = None
        self._world = None
        self._active = None
        self._founded = None
        self._guildhall = None
        self._open_applications = False
        self._active_war = None
        self._disband_date = None
        self._disband_condition = None
        self._homepage = None
        self._members = []
        self._invites = []

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def active(self, active: bool) -> Self:
        self._active = active
        return self

    def guildhall(self, guildhall: GuildHouse) -> Self:
        self._guildhall = guildhall
        return self

    def founded(self, founded: datetime.date) -> Self:
        self._founded = founded
        return self

    def open_applications(self, open_applications: bool) -> Self:
        self._open_applications = open_applications
        return self

    def active_war(self, active_war: bool) -> Self:
        self._active_war = active_war
        return self

    def disband_date(self, disband_date: Optional[datetime.date]) -> Self:
        self._disband_date = disband_date
        return self

    def disband_condition(self, disband_condition: Optional[str]) -> Self:
        self._disband_condition = disband_condition
        return self

    def homepage(self, homepage: Optional[str]) -> Self:
        self._homepage = homepage
        return self

    def members(self, members: List[GuildMember]) -> Self:
        self._members = members
        return self

    def add_member(self, member: GuildMember) -> Self:
        self._members.append(member)
        return self

    def invites(self, invites: List[GuildInvite]) -> Self:
        self._invites = invites
        return self

    def add_invite(self, invite: GuildInvite) -> Self:
        self._invites.append(invite)
        return self

    def build(self) -> Guild:
        return Guild(
            name=self._name,
            logo_url=self._logo_url,
            description=self._description,
            world=self._world,
            founded=self._founded,
            active=self._active,
            guildhall=self._guildhall,
            open_applications=self._open_applications,
            active_war=self._active_war,
            disband_date=self._disband_date,
            disband_condition=self._disband_condition,
            homepage=self._homepage,
            members=self._members,
            invites=self._invites,
        )


class GuildWarsBuilder:

    def __init__(self):
        self._name = None
        self._current = None
        self._history = None

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def current(self, current: Optional[GuildWarEntry]) -> Self:
        self._current = current
        return self

    def history(self, history: List[GuildWarEntry]) -> Self:
        self._history = history
        return self

    def build(self) -> GuildWars:
        return GuildWars(
            name=self._name,
            history=self._history,
            is_current=self._current,
        )


class GuildWarEntryBuilder:
    def __init__(self):
        self._guild_name = None
        self._guild_score = None
        self._guild_fee = None
        self._opponent_name = None
        self._opponent_score = None
        self._opponent_fee = None
        self._start_date = None
        self._score_limit = None
        self._duration = None
        self._end_date = None
        self._winner = None
        self._surrender = False

    def guild_name(self, guild_name: str) -> Self:
        self._guild_name = guild_name
        return self

    def guild_score(self, guild_score: int) -> Self:
        self._guild_score = guild_score
        return self

    def guild_fee(self, guild_fee: int) -> Self:
        self._guild_fee = guild_fee
        return self

    def opponent_name(self, opponent_name: Optional[str]) -> Self:
        self._opponent_name = opponent_name
        return self

    def opponent_score(self, opponent_score: int) -> Self:
        self._opponent_score = opponent_score
        return self

    def opponent_fee(self, opponent_fee: int) -> Self:
        self._opponent_fee = opponent_fee
        return self

    def start_date(self, start_date: Optional[datetime.date]) -> Self:
        self._start_date = start_date
        return self

    def score_limit(self, score_limit: int) -> Self:
        self._score_limit = score_limit
        return self

    def duration(self, duration: Optional[datetime.timedelta]) -> Self:
        self._duration = duration
        return self

    def end_date(self, end_date: Optional[datetime.date]) -> Self:
        self._end_date = end_date
        return self

    def winner(self, winner: Optional[str]) -> Self:
        self._winner = winner
        return self

    def surrender(self, surrender: bool) -> Self:
        self._surrender = surrender
        return self

    def build(self) -> GuildWarEntry:
        return GuildWarEntry(
            guild_name=self._guild_name,
            guild_score=self._guild_score,
            guild_fee=self._guild_fee,
            opponent_name=self._opponent_name,
            opponent_score=self._opponent_score,
            opponent_fee=self._opponent_fee,
            start_date=self._start_date,
            score_limit=self._score_limit,
            duration=self._duration,
            end_date=self._end_date,
            winner=self._winner,
            surrender=self._surrender,
        )
