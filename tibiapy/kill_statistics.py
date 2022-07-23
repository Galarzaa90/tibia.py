"""Models related to the kill statistics section in Tibia.com."""
from typing import Dict, List

from tibiapy import abc
from tibiapy.errors import InvalidContent
from tibiapy.utils import get_tibia_url, parse_form_data, parse_tibiacom_content

__all__ = (
    "KillStatistics",
    "RaceEntry",
)


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
    available_worlds: :class:`list` of :class:`str`
        The list of worlds available for selection.
    """

    __slots__ = (
        "world",
        "total",
        "entries",
        "available_worlds",
    )

    def __init__(self, world, entries=None, total=None, available_worlds=None):
        self.world: str = world
        self.entries: Dict[str, RaceEntry] = entries or {}
        self.total: RaceEntry = total or RaceEntry()
        self.available_worlds: List[str] = available_worlds or []

    @property
    def url(self):
        """:class:`str`: The URL to the kill statistics page on Tibia.com containing the results."""
        return self.get_url(self.world)

    @property
    def players(self):
        """:class:`RaceEntry`: The kill statistics for players."""
        return self.entries.get("players", RaceEntry())

    @classmethod
    def get_url(cls, world):
        """Get the Tibia.com URL of the kill statistics of a world.

        Parameters
        ----------
        world: :class:`str`
            The game world of the desired kill statistics.

        Returns
        -------
        The URL to the Tibia.com kill statistics for this world.
        """
        return get_tibia_url("community", "killstatistics", world=world)

    @classmethod
    def from_content(cls, content):
        """Create an instance of the class from the HTML content of the kill statistics' page.

        Parameters
        -----------
        content: :class:`str`
            The HTML content of the page.

        Returns
        ----------
        :class:`KillStatistics`
            The kill statistics contained in the page or None if it doesn't exist.

        Raises
        ------
        InvalidContent
            If content is not the HTML of a kill statistics' page.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            entries_table = parsed_content.find('table', attrs={'border': '0', 'cellpadding': '3'})
            form = parsed_content.find("form")
            data = parse_form_data(form, include_options=True)
            world = data["world"]
            available_worlds = list(data["__options__"]["world"].values())
            if not entries_table:
                entries_table = parsed_content.find("table", {"class": "Table3"})
            # If the entries table doesn't exist, it means that this belongs to an nonexistent or unselected world.
            if entries_table is None:
                return None
            header, subheader, *rows = entries_table.find_all('tr')
            entries = {}
            total = None
            for i, row in enumerate(rows):
                columns_raw = row.find_all('td')
                columns = [c.text.replace('\xa0', ' ').strip() for c in columns_raw]
                if not columns[2].isnumeric():
                    continue
                entry = RaceEntry(last_day_players_killed=int(columns[1]),
                                  last_day_killed=int(columns[2]),
                                  last_week_players_killed=int(columns[3]),
                                  last_week_killed=int(columns[4]))
                if i == len(rows) - 1:
                    total = entry
                else:
                    entries[columns[0]] = entry
            return cls(world, entries, total, available_worlds=available_worlds)
        except (AttributeError, KeyError) as e:
            raise InvalidContent("content does not belong to a Tibia.com kill statistics page.", e)


class RaceEntry(abc.Serializable):
    """Represents the statistics of a race.

    Attributes
    ----------
    last_day_killed: :class:`int`
        Number of creatures of this race killed in the last day.
    last_day_players_killed: :class:`int`
        Number of players killed by this race in the last day.
    last_week_killed: :class:`int`
        Number of creatures of this race killed in the last week.
    last_week_players_killed: :class:`int`
        Number of players killed by this race in the last week.
    """

    __slots__ = (
        "last_day_killed",
        "last_day_players_killed",
        "last_week_killed",
        "last_week_players_killed",
    )

    def __init__(self, last_day_killed=0, last_day_players_killed=0, last_week_killed=0, last_week_players_killed=0):
        self.last_day_killed: int = last_day_killed
        self.last_day_players_killed: int = last_day_players_killed
        self.last_week_killed: int = last_week_killed
        self.last_week_players_killed: int = last_week_players_killed

    def __repr__(self):
        return "<{0.__class__.__name__} last_day_killed={0.last_day_killed}" \
               " last_day_players_killed={0.last_day_players_killed} last_week_killed={0.last_week_killed}" \
               " last_week_players_killed={0.last_week_players_killed}>" \
            .format(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               self.last_day_killed == other.last_day_killed and \
               self.last_day_players_killed == other.last_day_players_killed and \
               self.last_week_killed == other.last_week_killed and \
               self.last_week_players_killed == other.last_week_players_killed
