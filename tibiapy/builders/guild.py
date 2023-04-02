from tibiapy.models import GuildEntry, Guild, GuildWars, GuildWarEntry


class _BaseGuildBuilder:

    def __init__(self, **kwargs):
        self._name = kwargs.get("name")

    def name(self, name):
        self._name = name
        return self

    def build(self):
        raise NotImplementedError


class GuildEntryBuilder(_BaseGuildBuilder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logo_url = kwargs.get("logo_url")
        self._description = kwargs.get("description")
        self._world = kwargs.get("world")
        self._active = kwargs.get("active")

    def logo_url(self, logo_url):
        self._logo_url = logo_url
        return self

    def description(self, description):
        self._description = description
        return self

    def world(self, world):
        self._world = world
        return self

    def active(self, active):
        self._active = active
        return self

    def build(self):
        return GuildEntry(
            name=self._name,
            logo_url=self._logo_url,
            description=self._description,
            world=self._world,
            active=self._active,
        )


class GuildBuilder(_BaseGuildBuilder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logo_url = kwargs.get("logo_url")
        self._description = kwargs.get("description")
        self._world = kwargs.get("world")
        self._active = kwargs.get("active")
        self._founded = kwargs.get("founded")
        self._guildhall = kwargs.get("guildhall")
        self._open_applications = kwargs.get("open_applications") or False
        self._active_war = kwargs.get("active_war")
        self._disband_date = kwargs.get("disband_date")
        self._disband_condition = kwargs.get("disband_condition")
        self._homepage = kwargs.get("homepage")
        self._members = kwargs.get("members") or []
        self._invites = kwargs.get("invites") or []

    def logo_url(self, logo_url):
        self._logo_url = logo_url
        return self

    def description(self, description):
        self._description = description
        return self

    def world(self, world):
        self._world = world
        return self

    def active(self, active):
        self._active = active
        return self

    def guildhall(self, guildhall):
        self._guildhall = guildhall
        return self

    def founded(self, founded):
        self._founded = founded
        return self

    def open_applications(self, open_applications):
        self._open_applications = open_applications
        return self

    def active_war(self, active_war):
        self._active_war = active_war
        return self

    def disband_date(self, disband_date):
        self._disband_date = disband_date
        return self

    def disband_condition(self, disband_condition):
        self._disband_condition = disband_condition
        return self

    def homepage(self, homepage):
        self._homepage = homepage
        return self

    def members(self, members):
        self._members = members
        return self

    def add_member(self, member):
        self._members.append(member)
        return self

    def invites(self, invites):
        self._invites = invites
        return self

    def add_invite(self, invite):
        self._invites.append(invite)
        return self

    def build(self):
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

    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._current = kwargs.get("current")
        self._history = kwargs.get("history")

    def name(self, name):
        self._name = name
        return self

    def current(self, current):
        self._current = current
        return self

    def history(self, history):
        self._history = history
        return self

    def build(self):
        return GuildWars(
            name=self._name,
            history=self._history,
            current=self._current,
        )


class GuildWarEntryBuilder:
    def __init__(self, **kwargs):
        self._guild_name = kwargs.get("guild_name")
        self._guild_score = kwargs.get("guild_score")
        self._guild_fee = kwargs.get("guild_fee")
        self._opponent_name = kwargs.get("opponent_name")
        self._opponent_score = kwargs.get("opponent_score")
        self._opponent_fee = kwargs.get("opponent_fee")
        self._start_date = kwargs.get("start_date")
        self._score_limit = kwargs.get("score_limit")
        self._duration = kwargs.get("duration")
        self._end_date = kwargs.get("end_date")
        self._winner = kwargs.get("winner")
        self._surrender = kwargs.get("surrender") or False

    def guild_name(self, guild_name):
        self._guild_name = guild_name
        return self

    def guild_score(self, guild_score):
        self._guild_score = guild_score
        return self

    def guild_fee(self, guild_fee):
        self._guild_fee = guild_fee
        return self

    def opponent_name(self, opponent_name):
        self._opponent_name = opponent_name
        return self

    def opponent_score(self, opponent_score):
        self._opponent_score = opponent_score
        return self

    def opponent_fee(self, opponent_fee):
        self._opponent_fee = opponent_fee
        return self

    def start_date(self, start_date):
        self._start_date = start_date
        return self

    def score_limit(self, score_limit):
        self._score_limit = score_limit
        return self

    def duration(self, duration):
        self._duration = duration
        return self

    def end_date(self, end_date):
        self._end_date = end_date
        return self

    def winner(self, winner):
        self._winner = winner
        return self

    def surrender(self, surrender):
        self._surrender = surrender
        return self

    def build(self):
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
