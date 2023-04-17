import datetime
from typing import List

from pydantic import BaseModel

from tibiapy.models import BaseCharacter
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.urls import get_leaderboards_url

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
    def url(self) -> str:
        """The URL to the current leaderboard."""
        return get_leaderboards_url(self.world, self.rotation.rotation_id, self.current_page)

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
        return get_leaderboards_url(self.world, self.rotation.rotation_id, page)
