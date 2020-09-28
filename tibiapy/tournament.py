import datetime
import math
import re
from typing import List

import bs4

from tibiapy import abc
from tibiapy.enums import PvpType, TournamentPhase, Vocation
from tibiapy.errors import InvalidContent
from tibiapy.utils import get_tibia_url, parse_integer, parse_popup, parse_tibia_datetime, parse_tibia_full_date, \
    parse_tibiacom_content, split_list, try_enum

__all__ = (
    "LeaderboardEntry",
    "ListedTournament",
    "RewardEntry",
    "RuleSet",
    "ScoreSet",
    "Tournament",
    "TournamentLeaderboard",
)

RANGE_PATTERN = re.compile(r'(\d+)(?:-(\d+))?')
CUP_PATTERN = re.compile(r'(\w+ cup)')
DEED_PATTERN = re.compile(r'(\w+ deed)')
ARCHIVE_LIST_PATTERN = re.compile(r'([\w\s]+)\s\(([^-]+)-\s([^)]+)\)')
RANK_PATTERN = re.compile(r'(\d+)\.\s\(\+?(-?\d+)\)')
RESULTS_PATTERN = re.compile(r'Results: (\d+)')
CURRENT_TOURNAMENT_PATTERN = re.compile(r'(?:.*- (\w+))')

TOURNAMENT_LEADERBOARDS_URL = "https://www.tibia.com/community/?subtopic=tournamentleaderboard"


class LeaderboardEntry(abc.BaseCharacter, abc.Serializable):
    """Represents a single tournament leaderboard's entry.

    .. versionadded:: 2.5.0

    Attributes
    ----------
    name: :class:`str`
        The character's name.
    rank: :class:`int`
        The entry's rank.
    change: :class:`int`
        The entry's change in rank since the last server save.
    vocation: :class:`Vocation`
        The character's vocation. This will always show the base vocation, without promotions.
    score: :class:`int`
        The entry's score.
    """

    __slots__ = (
        "name",
        "rank",
        "change",
        "vocation",
        "score",
    )

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.rank = kwargs.get("rank")
        self.change = kwargs.get("change")
        self.vocation = kwargs.get("vocation")
        self.score = kwargs.get("score")

    def __repr__(self):
        return "<{0.__class__.__name__} rank={0.rank} name={0.name!r} vocation={0.vocation!r} " \
               "points={0.score}>".format(self)


class ListedTournament(abc.BaseTournament, abc.Serializable):
    """Represents an tournament in the archived tournaments list.

    :py:attr:`start_date` and :py:attr:`end_date` might be :obj:`None` when a tournament that is currently running
    is on the list (e.g. on the leaderboards tournament selection section).

    .. versionadded:: 2.5.0

    Attributes
    ----------
    title: :class:`str`
        The title of the tournament.
    cycle: :class:`int`
        An internal number used to get direct access to a specific tournament in the archive.
    start_date: :class:`datetime.date`
        The start date of the tournament.
    end_date: :class:`datetime.date`
        The end date of the tournament.
    """

    __slots__ = (
        "title",
        "cycle",
        "start_date",
        "end_date",
    )

    _serializable_properties = ("duration",)

    def __init__(self, title, start_date, end_date, **kwargs):
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.cycle = kwargs.get("cycle", 0)

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} cycle={0.cycle} start_date={0.start_date!r} " \
               "end_date={0.end_date!r}>".format(self)

    @property
    def duration(self):
        """:class:`datetime.timedelta`: The total duration of the tournament."""
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None


class RewardEntry(abc.Serializable):
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
        self.initial_rank = kwargs.get("initial_rank", 0)
        self.last_rank = kwargs.get("last_rank", 0)
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
        return f"<{self.__class__.__name__}{attributes}>"


class RuleSet(abc.Serializable):
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
    shared_xp_bonus: :class:`bool`
        Whether there is a bonus for sharing experience or not.
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
        "shared_xp_bonus",
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
        self.shared_xp_bonus = kwargs.get("shared_xp_bonus")

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


class ScoreSet(abc.Serializable):
    """Represents the ways to earn or lose points in the tournament.

    .. versionadded:: 2.5.0

    Attributes
    ----------
    creature_kills: :class:`dict`
        Points received for participating in creature kills.
    level_gain_loss: :class:`int`
        The points gained for leveling up or lost for losing a level.
    skill_gain_loss: :class:`int`
        The points gained for leveling up or lost for losing a skill level.
    charm_point_multiplier: :class:`int`
        The multiplier for every charm point.
    character_death: :class:`int`
        The points lost for dying.
    area_discovery: :class:`int`
        Points that will be added to the score for discovering an area entirely.
    """

    __slots__ = (
        "creature_kills",
        "level_gain_loss",
        "skill_gain_loss",
        "charm_point_multiplier",
        "character_death",
        "area_discovery",
    )

    def __init__(self, **kwargs):
        self.creature_kills = kwargs.get("creature_kills", {})
        self.level_gain_loss = kwargs.get("level_gain_loss", 0)
        self.skill_gain_loss = kwargs.get("skill_gain_loss", 0)
        self.charm_point_multiplier = kwargs.get("charm_point_multiplier", 0)
        self.character_death = kwargs.get("character_death", 0)
        self.area_discovery = kwargs.get("area_discovery", 0)

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            v = getattr(self, attr)
            attributes += " %s=%r" % (attr, v)
        return "<{0.__class__.__name__}{1}>".format(self, attributes)


class Tournament(abc.BaseTournament, abc.Serializable):
    """Represents a tournament's information.

    .. versionadded:: 2.5.0

    Attributes
    ----------
    title: :class:`str`
        The title of the tournament.
    cycle: :class:`int`
        An internal number used to get direct access to a specific tournament in the archive.

        This will only be present when viewing an archived tournament, otherwise it will default to 0.
    phase: :class:`TournamentPhase`
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
        The list of rewards awarded for the specified ranges.
    archived_tournaments: :obj:`list` of :class:`ListedTournament`
        The list of other archived tournaments. This is only present when viewing an archived tournament.
    """

    __slots__ = (
        "phase",
        "start_date",
        "end_date",
        "worlds",
        "rule_set",
        "score_set",
        "reward_set",
        "archived_tournaments",
    )

    _serializable_properties = (
        "duration",
        "rewards_range",
    )

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.cycle = kwargs.get("cycle", 0)
        self.phase = try_enum(TournamentPhase, kwargs.get("phase"))
        self.start_date: datetime.datetime = kwargs.get("start_date")
        self.end_date: datetime.datetime = kwargs.get("end_date")
        self.worlds: List[str] = kwargs.get("worlds")
        self.rule_set: RuleSet = kwargs.get("rule_set")
        self.score_set: ScoreSet = kwargs.get("score_set")
        self.reward_set: List[RewardEntry] = kwargs.get("reward_set", [])
        self.archived_tournaments: List[ListedTournament] = kwargs.get("archived_tournaments", [])

    def __repr__(self):
        return "<{0.__class__.__name__} title={0.title!r} phase={0.phase!r} start_date={0.start_date!r} " \
               "end_date={0.start_date!r}>".format(self)

    @property
    def rewards_range(self):
        """:class:`tuple`:The range of ranks that might receive rewards."""
        return (self.reward_set[0].initial_rank, self.reward_set[-1].last_rank) if self.reward_set else (0, 0)

    @property
    def duration(self):
        """:class:`datetime.timedelta`: The total duration of the tournament."""
        return self.end_date - self.start_date

    def rewards_for_rank(self, rank):
        """Gets the rewards for a given rank, if any.

        Parameters
        ----------
        rank: :class:`int`
            The rank to check.

        Returns
        -------
        :class:`RewardEntry`, optional:
            The rewards for the given rank or None if there are no rewards.
        """
        for rewards in self.reward_set:
            if rewards.initial_rank <= rank <= rewards.last_rank:
                return rewards
        return None

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
            The tournament contained in the page, or None if the tournament doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a tournament's page.
        """
        try:
            if "An internal error has occurred" in content:
                return None
            if "Currently there is no Tournament running." in content:
                return None
            parsed_content = parse_tibiacom_content(content, builder='html5lib')
            box_content = parsed_content.find("div", attrs={"class": "BoxContent"})
            tables = box_content.find_all('table', attrs={"class": "Table5"})
            archive_table = box_content.find('table', attrs={"class": "Table4"})
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
            if archive_table:
                tournament._parse_archive_list(archive_table)
            return tournament
        except IndexError as e:
            raise InvalidContent("content does not belong to the Tibia.com's tournament section", e)

    def _parse_tournament_info(self, table):
        """Parses the tournament info table.

        Parameters
        ----------
        table: :class:`bs4.BeautifulSoup`
            The parsed table containing the tournament's information.
        """
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
            if field == "phase":
                value = try_enum(TournamentPhase, value)
            try:
                setattr(self, field, value)
            except AttributeError:
                pass

    def _parse_tournament_rules(self, table):
        """Parses the tournament rules table.

        Parameters
        ----------
        table: :class:`bs4.BeautifulSoup`
            The table containing the tournament rule set.
        """
        rows = table.find_all('tr')
        bool_fields = ("playtime_reduced_only_in_combat", "shared_xp_bonus")
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
            field, value, *_ = cols
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
        """Parses the tournament scores table.

        Parameters
        ----------
        table: :class:`bs4.BeautifulSoup`
            The parsed table containing the tournament score set.
        """
        creatures = {}
        rows = table.find_all('tr')
        rules = {}
        for row in rows[1:]:
            cols_raw = row.find_all('td')
            cols = [ele.text.strip() for ele in cols_raw]
            field, value, *_ = cols
            icon = cols_raw[2].find("span")
            field = field.replace("\xa0", "_").replace(" ", "_").replace(":", "").replace("/", "_").lower()
            value = re.sub(r'[^-0-9]', '', value.replace("+/-", ""))
            if not icon:
                creatures[field.replace("_", " ")] = int(value)
            else:
                rules[field] = parse_integer(value)
        if "creature_kills" in rules:
            rules["creature_kills"] = creatures
        self.score_set = ScoreSet(**rules)

    def _parse_tournament_rewards(self, table):
        """Parses the reward section of the tournament information section.

        Parameters
        ----------
        table: :class:`bs4.BeautifulSoup`
            The parsed table containing the information.
        """
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
                self._parse_rewards_column(col, entry)
            rewards.append(entry)
        self.reward_set = rewards

    @classmethod
    def _parse_rewards_column(cls, column, entry):
        """Parses a column from the tournament's reward section.

        Parameters
        ----------
        column: :class:`bs4.BeautifulSoup`
            The parsed content of the column.
        entry: :class:`RewardEntry`
            The reward entry where the data will be stored to.
        """
        col_str = str(column)
        img = column.find('img')
        if img and "tibiacoin" in img["src"]:
            entry.tibia_coins = parse_integer(column.text)
        if img and "tournamentcoin" in img["src"]:
            entry.tournament_coins = parse_integer(column.text)
        if img and "tournamentvoucher" in img["src"]:
            entry.tournament_ticker_voucher = parse_integer(column.text)
        if img and "trophy" in img["src"]:
            m = CUP_PATTERN.search(col_str)
            if m:
                entry.cup = m.group(1)
            m = DEED_PATTERN.search(col_str)
            if m:
                entry.deed = m.group(1)
        if img and "reward" in img["src"]:
            span = column.find('span', attrs={"class": "HelperDivIndicator"})
            mouse_over = span["onmouseover"]
            title, popup = parse_popup(mouse_over)
            label = popup.find('div', attrs={'class': 'ItemOverLabel'})
            entry.other_rewards = label.text.strip()

    @staticmethod
    def _parse_rank_range(rank_text):
        """Parses the rank range text from the reward set table.

        Parameters
        ----------
        rank_text: :class:`str`
            The string describing the ranks.

        Returns
        -------
        :class:`tuple` of :class:`int`
            A tuple containing the highest and lower rank for this reward bracket.

            If the reward is for a single rank, both tuple elements will be the same.
        """
        m = RANGE_PATTERN.search(rank_text)
        first = int(m.group(1))
        last = first
        if m.group(2):
            last = int(m.group(2))
        return first, last

    def _parse_archive_list(self, archive_table):
        """Parses the archive list table.

        This table is only visible when viewing a tournament from the archive.

        Parameters
        ----------
        archive_table: :class:`bs4.Tag`
            The parsed element containing the table.
        """
        _, *options = archive_table.find_all("option")
        self.archived_tournaments = []
        for option in options:
            m = ARCHIVE_LIST_PATTERN.match(option.text)
            if not m:
                continue
            title = m.group(1).strip()
            start_date = parse_tibia_full_date(m.group(2))
            end_date = parse_tibia_full_date(m.group(3))
            value = int(option["value"])
            if title == self.title:
                self.cycle = value
            self.archived_tournaments.append(ListedTournament(title=title, start_date=start_date, end_date=end_date,
                                                              cycle=value))


class TournamentLeaderboard(abc.Serializable):
    """Represents a tournament's leaderboards.

    .. versionadded:: 2.5.0

    Attributes
    ----------
    world: :class:`str`
        The world this leaderboard belongs to.
    tournament: :class:`ListedTournament`
        The tournament this leaderboard belongs to.
    entries: :obj:`list` of :class:`LeaderboardEntry`
        The leaderboard entries.
    results_count: :class:`int`
        The total number of leaderboard entries. These might be in a different page.
    """

    ENTRIES_PER_PAGE = 100

    __slots__ = (
        "world",
        "tournament",
        "entries",
        "results_count",
    )

    _serializable_properties = (
        "page",
        "total_pages"
    )

    def __init__(self, **kwargs):
        self.world: str = kwargs.get("world")
        self.tournament: ListedTournament = kwargs.get("tournament")
        self.entries: List[LeaderboardEntry] = kwargs.get("entries", [])
        self.results_count = kwargs.get("results_count", 0)

    def __repr__(self):
        return f"<{self.__class__.__name__} world={self.world!r} tournament={self.tournament} " \
               f"results_count={self.results_count}>"

    @property
    def from_rank(self):
        """:class:`int`: The starting rank of the provided entries."""
        return self.entries[0].rank if self.entries else 0

    @property
    def to_rank(self):
        """:class:`int`: The last rank of the provided entries."""
        return self.entries[-1].rank if self.entries else 0

    @property
    def page(self):
        """:class:`int`: The page number the shown results correspond to on Tibia.com"""
        return int(math.floor(self.from_rank / self.ENTRIES_PER_PAGE)) + 1 if self.from_rank else 0

    @property
    def total_pages(self):
        """:class:`int`: The total of pages in the leaderboard."""
        return int(math.ceil(self.results_count / self.ENTRIES_PER_PAGE))

    @property
    def url(self):
        """:class:`str`: Gets the URL to the current leaderboard and page."""
        return self.get_url(self.world, self.tournament.cycle, self.page)

    @classmethod
    def get_url(cls, world, tournament_cycle, page=1):
        """Gets the URL to the leaderboards of a specific world, tournament and page.

        Parameters
        ----------
        world: :class:`str`
            The world to get the leaderboards for.
        tournament_cycle: :class:`int`
            The cycle of the tournament to get the leaderboards for.
        page: :class:`int`
            The leader board's page to view. By default 1.

        Returns
        -------
        The URL to the specified leaderboard.
        """
        return get_tibia_url("community", "tournamentleaderboards", tournamentworld=world,
                             tournamentcycle=tournament_cycle, selectedleaderboardpage=page)

    @classmethod
    def from_content(cls, content):
        """Creates an instance of the class from the html content of the tournament's leaderboards page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        -------
        :class:`TournamentLeaderboard`
            The tournament contained in the page, or None if the tournament leaderboard doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a tournament's leaderboard page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.find_all('div', attrs={'class': 'TableContainer'})
            if not tables:
                raise InvalidContent("content does not belong to the Tibia.com's tournament leaderboards section")
            selector_table = tables[0]
            leaderboard = cls()
            result = leaderboard._parse_leaderboard_selectors(selector_table)
            if not result:
                return None
            ranking_table = tables[1]
            leaderboard._parse_leaderboard_entries(ranking_table)
            return leaderboard
        except AttributeError as e:
            raise InvalidContent("content does not belong to the Tibia.com's tournament leaderboards section", e)

    def _parse_leaderboard_selectors(self, selector_table):
        """Parses the option selectors from the leaderboards to get their information.

        Parameters
        ----------
        selector_table: :class:`bs4.BeautifulSoup`

        Returns
        -------
        :class:`bool`
            Whether the selectors could be parsed or not.
        """
        world_select = selector_table.find("select", attrs={"name": "tournamentworld"})
        selected_world = world_select.find("option", {"selected": "selected"})
        if not selected_world:
            return False
        self.world = selected_world.text
        tournament_select = selector_table.find("select", attrs={"name": "tournamentcycle"})
        selected_tournament = tournament_select.find("option", {"selected": "selected"})
        tournament_text = selected_tournament.text
        start_date = None
        end_date = None
        cycle = int(selected_tournament["value"])
        if "current tournament" in tournament_text.lower():
            tournament_title = CURRENT_TOURNAMENT_PATTERN.sub(r"\g<1>", tournament_text)
        else:
            m = ARCHIVE_LIST_PATTERN.search(tournament_text)
            tournament_title = m.group(1).strip()
            start_date = parse_tibia_full_date(m.group(2))
            end_date = parse_tibia_full_date(m.group(3))
        self.tournament = ListedTournament(title=tournament_title, start_date=start_date, end_date=end_date,
                                           cycle=cycle)
        return True

    def _parse_leaderboard_entries(self, ranking_table):
        """Parses the leaderboards' entries.

        Parameters
        ----------
        ranking_table: :class:`bs4.BeautifulSoup`
            The table containing the rankings.
        """
        ranking_table_content = ranking_table.find("table", attrs={"class": "TableContent"})
        header, *rows = ranking_table_content.find_all('tr')
        entries = []
        for row in rows:
            raw_columns = row.find_all("td")
            if len(raw_columns) != 4:
                break
            cols = [c.text.strip() for c in raw_columns]
            rank_and_change, character, vocation, score = cols
            m = RANK_PATTERN.search(rank_and_change)
            rank = int(m.group(1))
            change = int(m.group(2))
            voc = try_enum(Vocation, vocation)
            score = parse_integer(score, 0)
            entries.append(LeaderboardEntry(rank=rank, change=change, name=character, vocation=voc, score=score))
        # Results footer
        small = ranking_table.find("small")
        if small:
            pagination_text = small.text
            results_str = RESULTS_PATTERN.search(pagination_text)
            self.results_count = int(results_str.group(1))
        self.entries = entries
