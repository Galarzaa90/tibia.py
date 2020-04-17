import datetime
import re
from typing import List

import bs4

from tibiapy import abc, PvpType
from tibiapy.utils import parse_integer, parse_tibia_datetime, parse_tibiacom_content, split_list, try_enum

__all__ = (
    "Tournament",
    "RuleSet",
    "ScoreSet",
    "RewardEntry",
)

RANGE_PATTERN = re.compile(r'(\d+)(?:-(\d+))?')
CUP_PATTERN = re.compile(r'(\w+ cup)')
DEED_PATTERN = re.compile(r'(\w+ deed)')


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
    worlds: :obj:`list` of :class:`str`
        The worlds where this tournament is active on.
    rule_set: :class:`RuleSet`
        The specific rules for this tournament.
    score_set: :class:`ScoreSet`
        The ways to gain points in the tournament.
    reward_set: :obj:`list` of :class:`RewardEntry`
    """

    __slots__ = (
        "title",
        "phase",
        "start_date",
        "end_date",
        "worlds",
        "rule_set",
        "score_set",
        "reward_set",
    )

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.phase = kwargs.get("phase")
        self.start_date = kwargs.get("start_date")  # type: datetime.datetime
        self.end_date = kwargs.get("end_date")  # type: datetime.datetime
        self.worlds = kwargs.get("worlds")  # type: List[str]
        self.rule_set = kwargs.get("rule_set")  # type: RuleSet
        self.score_set = kwargs.get("score_set")  # type: ScoreSet
        self.reward_set = kwargs.get("reward_set", [])  # type: List[RewardEntry]

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
            box_content = parsed_content.find("div", attrs={"class": "BoxContent"})
            tables = box_content.find_all('table', attrs={"class": "Table5"})
            tournament_details_table = tables[-1]
            info_tables = tournament_details_table.find_all('table', attrs={'class': 'TableContent'})
            main_info = info_tables[0]
            rule_set = info_tables[1]
            score_set = info_tables[2]
            reward_set = info_tables[3]
            tournament = cls()
            tournament._parse_tournament_info(main_info)
            tournament._parse_tournament_rules(rule_set)
            tournament._parse_tournament_scores(score_set)
            tournament._parse_tournament_rewards(reward_set)
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

    def _parse_tournament_scores(self, table):
        rows = table.find_all('tr')
        rules = {}
        for row in rows[1:]:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value, *_ = cols
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").replace("/", "_").lower()
            value = re.sub(r'[^-0-9]', '', value.replace("+/-",""))
            rules[field] = parse_integer(value)
        self.score_set = ScoreSet(**rules)

    def _parse_tournament_rewards(self, table):
        rows = table.find_all('tr')
        rewards = []
        for row in rows[1:]:
            cols_raw = row.find_all('td')
            rank_row, *rewards_cols = cols_raw
            rank_text = rank_row.text
            if not rank_text:
                break
            first, last = self._parse_rank_range(rank_text)
            entry = RewardEntry(initial_rank=first, last_rank=last)
            for col in rewards_cols:
                col_str = str(col)
                img = col.find('img')
                if img and "tibiacoin" in img["src"]:
                    entry.tibia_coins = parse_integer(col.text)
                if img and "tournamentcoin" in img["src"]:
                    entry.tournament_coins = parse_integer(col.text)
                if img and "tournamentvoucher" in img["src"]:
                    entry.tournament_ticker_voucher = parse_integer(col.text)
                if img and "trophy" in img["src"]:
                    m = CUP_PATTERN.search(col_str)
                    if m:
                        entry.cup = m.group(1)
                    m = DEED_PATTERN.search(col_str)
                    if m:
                        entry.deed = m.group(1)
                if img and "reward" in img["src"]:
                    span = col.find('span', attrs={"class": "HelperDivIndicator"})
                    mouse_over = span["onmouseover"]
                    title, popup = self._parse_popup(mouse_over)
                    label = popup.find('div', attrs={'class': 'ItemOverLabel'})
                    entry.other_rewards = label.text.strip()
            rewards.append(entry)
        self.reward_set = rewards

    @staticmethod
    def _parse_popup(popup_content):
        parts = popup_content.split(",", 2)
        title = parts[1].replace(r"'", "").strip()
        html = parts[-1].replace(r"\'",'"').replace(r"'", "").replace(",);","").strip()
        parsed_html = bs4.BeautifulSoup(html, 'lxml')
        return title, parsed_html

    @staticmethod
    def _parse_rank_range(rank_text):
        m = RANGE_PATTERN.search(rank_text)
        first = int(m.group(1))
        last = first
        if m.group(2):
            last = int(m.group(2))
        return first, last


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
        try:
            t = datetime.datetime.strptime(interval, "%H:%M:%S")
            return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        except ValueError:
            return None


class ScoreSet:
    """Represents the ways to earn or lose points in the tournament.

    Attributes
    ----------
    level_gain_loss: :class:`int`
        The points gained for leveling up or lost for losing a level.
    charm_point_multiplier: :class:`int`
        The multiplier for every charm point.
    character_death: :class:`int`
        The points lost for dying.
    """

    __slots__ = (
        "level_gain_loss",
        "charm_point_multiplier",
        "character_death",
    )

    def __init__(self, **kwargs):
        self.level_gain_loss = kwargs.get("level_gain_loss", 0)
        self.charm_point_multiplier = kwargs.get("charm_point_multiplier", 0)
        self.character_death = kwargs.get("character_death", 0)

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            v = getattr(self, attr)
            attributes += " %s=%r" % (attr, v)
        return "<{0.__class__.__name__}{1}>".format(self, attributes)


class RewardEntry:
    """Represents the rewards for a specific rank range.

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
    tournament_ticket_voucher: :class:`int`
        The amount of tournament ticker vouchers awarded.
    cup: :class:`str`
        The type of cup awarded.
    deed: :class:`str`
        The type of deed awarded.
    other_rewards: :class:`str`
        Other rewards given for this rank.
    """

    __slots__ = (
        "initial_rank",
        "last_rank",
        "tibia_coins",
        "tournament_coins",
        "tournament_ticker_voucher",
        "cup",
        "deed",
        "other_rewards",
    )

    def __init__(self, **kwargs):
        self.initial_rank = kwargs.get("initial_rank")
        self.last_rank = kwargs.get("last_rank")
        self.tibia_coins = kwargs.get("tibia_coins", 0)
        self.tournament_coins = kwargs.get("tournament_coins", 0)
        self.tournament_ticker_voucher = kwargs.get("tournament_ticker_voucher", 0)
        self.cup = kwargs.get("cup")
        self.deed = kwargs.get("deed")
        self.other_rewards = kwargs.get("other_rewards")

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            v = getattr(self, attr)
            attributes += " %s=%r" % (attr, v)
        return "<{0.__class__.__name__}{1}>".format(self, attributes)
