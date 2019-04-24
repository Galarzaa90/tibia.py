from tibiapy import abc
from tibiapy.utils import parse_tibiacom_content

KILL_STATISTICS_URL = "https://www.tibia.com/community/?subtopic=killstatistics&world=%s"


class KillStatistics(abc.Serializable):
    """Represents the kill statistics of a world.

    Attributes
    ----------
    world: :class:`str`
        The world the statistics belong to.
    entries: :class:`dict`
        A dictionary of kills entries of every race, where the key is the name of the race.
    total: :class:`RaceEntry`
        The kill statistics totals.
    """
    __slots__ = ("world", "entries", "total")

    def __init__(self, world, entries=None, total=None):
        self.world = world
        self.entries = entries or []
        self.total = total

    @property
    def url(self):
        return self.get_url(self.world)

    @classmethod
    def get_url(cls, world):
        return KILL_STATISTICS_URL % world

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content)
        selection_table = parsed_content.find('div', attrs={'class': 'TableContainer'})
        world = selection_table.find("option", {"selected": True})["value"]

        entries_table = parsed_content.find('table', attrs={'border': '0', 'cellpadding': '3'})
        header, subheader, *rows = entries_table.find_all('tr')
        entries = {}
        total = None
        for i, row in enumerate(rows):
            columns_raw = row.find_all('td')
            columns = [c.text.replace('\xa0', ' ').strip() for c in columns_raw]
            entry = RaceEntry(last_day=TimeEntry(int(columns[1]), int(columns[2])),
                              last_week=TimeEntry(int(columns[3]), int(columns[4])))
            if i == len(rows) - 1:
                total = entry
            else:
                entries[columns[0]] = entry
        return cls(world, entries, total)


class RaceEntry(abc.Serializable):
    """Represents the statistics of a race.

    Attributes
    ----------
    last_day: :class:`TimeEntry`
        The statistics for this race in the last day.
    last_week: :class:`TimeEntry`
        The statistics for this race in the last week.
    """
    __slots__ = ("last_day", "last_week")

    def __init__(self, last_day=None, last_week=None):
        self.last_day = last_day
        self.last_week = last_week

    def __repr__(self):
        return "<{0.__class__.__name__} last_day={0.last_day!r} last_week={0.last_week!r}>" \
            .format(self)


class TimeEntry(abc.Serializable):
    """Represents the statistics of a time entry.

    Attributes
    ----------
    killed_players: :class:`int`
        The number of players this race killed.
    killed_by_players: :class:`int`
        The number of player kills of this race.
    """
    __slots__ = ("killed_players", "killed_by_players")

    def __init__(self, killed_players=0, killed_by_players=0):
        self.killed_players = killed_players
        self.killed_by_players = killed_by_players

    def __repr__(self):
        return "<{0.__class__.__name__} killed_players={0.killed_players} killed_by_players={0.killed_by_players}>" \
            .format(self)
