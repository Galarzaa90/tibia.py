import datetime

from tibiapy import abc, PvpType
from tibiapy.utils import parse_tibiacom_content, parse_tibia_datetime, split_list, try_enum


class Tournament(abc.Serializable):
    """Represents a tournament's information.

    Attributes
    ----------
    title: :class:`str`
        The title of the tournament.
    phase: :class:`str`
        The current phase of the tournament.
    start_date: :class:`datetime.datetime`
        The start date of the tournament.
    end_date: :class:`datetime.datetime`
        The end date of the tournament.
    worlds: :obj:`list` of :class:`str`.
        The worlds where this tournament is active on.
    rule_set: :class:`RuleSet`
        The specific rules for this tournament.
    """

    __slots__ = (
        "title",
        "phase",
        "start_date",
        "end_date",
        "worlds",
        "rule_set",
    )

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.phase = kwargs.get("phase")
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")
        self.worlds = kwargs.get("worlds")
        self.rule_set = kwargs.get("rule_set")

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} phase={0.phase!r} start_date={0.start_date!r} " \
               "end_date={0.start_date!r}>".format(self)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of the tournament's page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`Tournament`
            The tournament contained in the page, or None if the tournament doesn't exist

        Raises
        ------
        InvalidContent
            If content is not the HTML of a tournament's page.
        """
        try:
            parsed_content = parse_tibiacom_content(content, builder='html5lib')
            tables = parsed_content.find_all('table', attrs={"class": "Table5"})
            tournament_details_table = tables[1]
            info_tables = tournament_details_table.find_all('table', attrs={'class': 'TableContent'})
            main_info = info_tables[0]
            rule_set = info_tables[1]
            tournament = cls()
            tournament._parse_tournament_info(main_info)
            tournament._parse_tournament_rules(rule_set)
            return tournament
        except Exception:
            raise

    def _parse_tournament_info(self, table):
        rows = table.find_all('tr')
        date_fields = ("start_date", "end_date")
        list_fields = ("worlds",)
        for row in rows:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            if field in date_fields:
                value = parse_tibia_datetime(value)
            if field in list_fields:
                value = split_list(value, ",", ",")
            try:
                setattr(self, field, value)
            except AttributeError:
                pass

    def _parse_tournament_rules(self, table):
        rows = table.find_all('tr')
        bool_fields = ("playtime_reduced_only_in_combat",)
        float_fields = (
            "death_penalty_modifier",
            "xp_multiplier",
            "skill_multiplier",
            "spawn_rate_multiplier",
            "loot_probability"
        )
        int_fields = ("rent_percentage", "house_auction_durations")
        rules = {}
        for row in rows[1:]:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").lower()
            value = value.replace("\xa0", " ")
            if field in bool_fields:
                value = value.lower() == "yes"
            if field in float_fields:
                value = float(value.replace("x", ""))
            if field in int_fields:
                value = int(value.replace("%", ""))
            rules[field] = value
        self.rule_set = RuleSet(**rules)


class RuleSet:
    """Contains the tournament rule set.

    Attributes
    ----------
    pvp_type: :class:`PvPType`
        The PvP type of the tournament.
    daily_tournament_playtime: :class:`datetime.timedelta`
        The maximum amount of time participants can play each day.
    total_tournament_playtime: :class:`datetime.timedelta`
        The total amount of time participants can play in the tournament.
    playtime_reduced_only_in_combat: :class:`bool`
        Whether playtime will only be reduced while in combat or not.
    death_penalty_modifier: :class:`float`
        The modifier for the death penalty.
    xp_multiplier: :class:`float`
        The multiplier for experience gained.
    skill_multiplier: :class:`float`
        The multiplier for skill gained.
    spawn_rate_multiplier: :class:`float`
        The multiplier for the spawn rate.
    loot_probability: :class:`float`
        The multiplier for the loot rate.
    rent_percentage: :class:`int`
        The percentage of rent prices relative to the regular price.
    house_auction_durations: :class:`int`
        The duration of house auctions.
    """

    __slots__ = (
        "pvp_type",
        "daily_tournament_playtime",
        "total_tournament_playtime",
        "playtime_reduced_only_in_combat",
        "death_penalty_modifier",
        "xp_multiplier",
        "skill_multiplier",
        "spawn_rate_multiplier",
        "loot_probability",
        "rent_percentage",
        "house_auction_durations",
    )

    def __init__(self, **kwargs):
        self.pvp_type = try_enum(PvpType, kwargs.get("pvp_type"))
        self.daily_tournament_playtime = self._try_parse_interval(kwargs.get("daily_tournament_playtime"))
        self.total_tournament_playtime = self._try_parse_interval(kwargs.get("total_tournament_playtime"))
        self.playtime_reduced_only_in_combat = kwargs.get("playtime_reduced_only_in_combat")
        self.death_penalty_modifier = kwargs.get("death_penalty_modifier")
        self.xp_multiplier = kwargs.get("xp_multiplier")
        self.skill_multiplier = kwargs.get("skill_multiplier")
        self.spawn_rate_multiplier = kwargs.get("spawn_rate_multiplier")
        self.loot_probability = kwargs.get("loot_probability")
        self.rent_percentage = kwargs.get("rent_percentage")
        self.house_auction_durations = kwargs.get("house_auction_durations")

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            v = getattr(self, attr)
            attributes += " %s=%r" % (attr, v)
        return "<{0.__class__.__name__}{1}>".format(self, attributes)

    @staticmethod
    def _try_parse_interval(interval):
        if interval is None:
            return None
        if isinstance(interval, datetime.timedelta):
            return interval
        t = datetime.datetime.strptime(interval, "%H:%M:%S")
        return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

class ScoreSet:
    """

    Attributes
    ----------
    level_gain_loss: :class:`int`
        The points gained for leveling up or lost for losing a level.
    charm_point_multiplier: :class:`int`
        The multiplier for every charm point.
    character_death: :class:`int`
        The points lost for dying.
    """

class RewardEntry:
    """

    Attributes
    ----------
    initial_rank: :class:`int`
        The highest rank that gets this reward.
    last_rank: :class:`int`
        The lowest rank that gets this reward.
    tibia_coins: :class`int`
        The amount of tibia coins awarded.
    tournament_coins: :class:`int`
        The amount of tournament coins awarded.
    cup: :class:`str`
        The type of cup awarded.
    deed: :class:`str`
        The type of deed awarded.
    other_rewards: :class:`str`
        Other rewards given for this rank.
    """

    def __init__(self):
        pass
