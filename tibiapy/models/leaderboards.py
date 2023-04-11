import datetime
from typing import List

from pydantic import BaseModel

from tibiapy.models import BaseCharacter
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.utils import get_tibia_url


__all__ = (
    'LeaderboardEntry',
    'LeaderboardRotation',
    'Leaderboard',
)


class LeaderboardEntry(BaseCharacter):
    rank: int
    """The rank of this entry."""
    drome_level: int
    """The Tibia Drome level of this entry."""


class LeaderboardRotation(BaseModel):
    rotation_id: int
    """The internal ID of the rotation."""
    current: bool
    """Whether this is the currently running rotation or not."""
    end_date: datetime.datetime
    """The date and time when this rotation ends."""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.rotation_id == self.rotation_id
        return False


class Leaderboard(PaginatedWithUrl[LeaderboardEntry]):
    """Represents the Tibiadrome leaderboards."""

    world: str
    """The world this leaderboards are for."""
    available_worlds: List[str]
    """The worlds available for selection."""
    rotation: LeaderboardRotation
    """The rotation this leaderboards' entries are for."""
    available_rotations: List[LeaderboardRotation]
    """The available rotations for selection."""
    last_update: datetime.timedelta
    """How long ago was the currently displayed data updated. Only available for the current rotation."""

    @property
    def url(self):
        """:class:`str`: The URL to the current leaderboard."""
        return self.get_url(self.world, self.rotation.rotation_id, self.current_page)

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