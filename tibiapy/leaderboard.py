"""Models related to the leaderboard section in Tibia.com."""
import datetime
import re
from typing import List, Optional

from tibiapy import abc, errors
from tibiapy.utils import get_tibia_url, parse_form_data, parse_pagination, parse_tibia_datetime, parse_tibiacom_content

__all__ = (
    'Leaderboard',
    'LeaderboardEntry',
    'LeaderboardRotation',
)

rotation_end_pattern = re.compile(r"ends on ([^)]+)")


class Leaderboard(abc.Serializable):
    """Represents the Tibiadrome leaderboards.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    world: :class:`str`
        The world this leaderboards are for.
    available_worlds: :class:`list` of :class:`str`
        The worlds available for selection.
    rotation: :class:`LeaderboardRotation`
        The rotation this leaderboards' entries are for.
    available_rotations: :class:`list` of :class:`LeaderboardRotation`
        The available rotations for selection.
    entries: list of :class:`LeaderboardEntry`
        The list of entries in this leaderboard.
    last_update: :class:`datetime.timedelta`
        How long ago was the currently displayed data updated. Only available for the current rotation.
    page: :class:`int`
        The page number being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results_count: :class:`int`
        The total amount of entries in this rotation. These may be shown in another page.
    """

    __slots__ = (
        "world",
        "rotation",
        "last_update",
        "page",
        "total_pages",
        "results_count",
        "entries",
        "available_worlds",
        "available_rotations",
    )

    def __init__(self, world, rotation, **kwargs):
        self.world: str = world
        self.rotation: LeaderboardRotation = rotation
        self.available_worlds: List[str] = kwargs.get("available_worlds", [])
        self.available_rotations: List[LeaderboardRotation] = kwargs.get("available_rotations", [])
        self.entries: List[LeaderboardEntry] = kwargs.get("entries", [])
        self.last_update: Optional[datetime.timedelta] = kwargs.get("last_update")
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.results_count: int = kwargs.get("results_count", 0)

    def __repr__(self):
        return f"<{self.__class__.__name__} world={self.world!r} rotation={self.rotation!r} " \
               f"page={self.page!r} total_pages={self.total_pages!r} results_count={self.results_count!r}>"

    @property
    def url(self):
        """:class:`str`: The URL to the current leaderboard."""
        return self.get_url(self.world, self.rotation.rotation_id, self.page)

    @property
    def previous_page_url(self):
        """:class:`str`: The URL to the previous page of the current leaderboard results, if there's any."""
        return self.get_page_url(self.page - 1) if self.page > 1 else None

    @property
    def next_page_url(self):
        """:class:`str`: The URL to the next page of the current leaderboard results, if there's any."""
        return self.get_page_url(self.page + 1) if self.page < self.total_pages else None

    def get_page_url(self, page):
        """Get the URL of the leaderboard at a specific page, with the current date parameters.

        Parameters
        ----------
        page: :class:`int`
            The desired page.

        Returns
        -------
        :class:`str`
            The URL to the desired page.

        Raises
        ------
        ValueError
            If the specified page is zer or less.
        """
        return self.get_url(self.world, self.rotation.rotation_id, page)

    @classmethod
    def get_url(cls, world, rotation_id=None, page=1):
        """Get the URL to the leaderboards of a world.

        Parameters
        ----------
        world: :class:`str`
            The desired world.
        rotation_id: :class:`int`
            The ID of the desired rotation. If undefined, the current rotation is shown.
        page: :class:`int`
            The desired page. By default, the first page is returned.

        Returns
        -------
        :class:`str`
            The URL to the leaderboard with the desired parameters.

        Raises
        ------
        ValueError
            If the specified page is zer or less.
        """
        if page <= 0:
            raise ValueError("page must be 1 or greater")
        return get_tibia_url("community", "leaderboards", world=world, rotation=rotation_id, currentpage=page)

    @classmethod
    def from_content(cls, content):
        """Parse the content of the leaderboards page.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the leaderboards page.

        Returns
        -------
        :class:`Leaderboard`
            The ledaerboard if found.
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parsed_content.find_all("table", {"class": "TableContent"})
            form = parsed_content.find("form")
            data = parse_form_data(form, include_options=True)
            current_world = data["world"]
            current_rotation = None
            rotations = []
            for label, value in data["__options__"]["rotation"].items():
                current = False
                if "Current" in label:
                    label = "".join(rotation_end_pattern.findall(label))
                    current = True
                rotation_end = parse_tibia_datetime(label)
                rotation = LeaderboardRotation(int(value), rotation_end, current)
                if value == data["rotation"]:
                    current_rotation = rotation
                rotations.append(rotation)
            leaderboard = cls(current_world, current_rotation)
            leaderboard.available_worlds = [w for w in data["__options__"]["world"].values() if w]
            leaderboard.available_rotations = rotations
            if leaderboard.rotation and leaderboard.rotation.current:
                last_update_table = tables[2]
                numbers = re.findall(r'(\d+)', last_update_table.text)
                if numbers:
                    leaderboard.last_update = datetime.timedelta(minutes=int(numbers[0]))
            leaderboard._parse_entries(tables[-1])
            pagination_block = parsed_content.find("small")
            pages, total, count = parse_pagination(pagination_block) if pagination_block else (0, 0, 0)
            leaderboard.page = pages
            leaderboard.total_pages = total
            leaderboard.results_count = count
            return leaderboard
        except (AttributeError, ValueError, KeyError) as e:
            raise errors.InvalidContent("content does not belong to the leaderboards", e)

    def _parse_entries(self, entries_table):
        entries_rows = entries_table.find_all("tr", {'style': True})
        for row in entries_rows:
            columns_raw = row.find_all("td")
            cols = [c.text for c in columns_raw]
            rank, name, points = cols
            entry = LeaderboardEntry(int(rank.replace(".", "")), name, int(points))
            self.entries.append(entry)


class LeaderboardEntry(abc.BaseCharacter, abc.Serializable):
    """Represents a single leadeboard entry.

    Parameters
    ----------
    rank: :class:`int`
        The rank of this entry.
    name: :class:`str`
        The name of the character.
    drome_level: :class:`int`
        The Tibia Drome level of this entry.
    """

    __slots__ = (
        "rank",
        "name",
        "drome_level",
    )

    def __init__(self, rank, name, drome_level):
        self.rank: int = rank
        self.name: str = name
        self.drome_level: int = drome_level

    def __repr__(self):
        return f"<{self.__class__.__name__} rank={self.rank} name={self.name!r} drome_level={self.drome_level}>"


class LeaderboardRotation(abc.Serializable):
    """A leaderboard rotation.

    .. versionadded:: 5.0.0

    Parameters
    ----------
    rotation_id: :class:`int`
        The internal ID of the rotation.
    current: :class:`bool`
        Whether this is the currently running rotation or not.
    end_date: :class:`datetime.datetime`
        The date and time when this rotation ends.
    """

    __slots__ = (
        "rotation_id",
        "current",
        "end_date",
    )

    def __init__(self, rotation_id, end_date, current=False):
        self.rotation_id: int = rotation_id
        self.end_date: datetime.datetime = end_date
        self.current: bool = current

    def __repr__(self):
        return f"<{self.__class__.__name__} rotation_id={self.rotation_id} end_date={self.end_date!r} " \
               f"current={self.current!r}>"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.rotation_id == self.rotation_id
        return False
