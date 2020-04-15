from tibiapy import abc
from tibiapy.utils import parse_tibiacom_content, parse_tibia_datetime, split_list


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
            rows = main_info.find_all('tr')
            date_fields = ("start_date", "end_date")
            list_fields = ("worlds",)
            tournament = cls()
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
                    setattr(tournament, field, value)
                except AttributeError:
                    pass
            return tournament
        except Exception:
            raise

class RuleSet:
    """

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
    house_auction_duration: :class:`int`
        The duration of house auctions.
    """

    def __init__(self):
        pass

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
