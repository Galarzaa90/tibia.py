"""Models related to the leaderboards."""
import datetime
from typing import Any, List, Optional

from tibiapy.models import BaseModel
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.urls import get_leaderboards_url, get_character_url

__all__ = (
    "LeaderboardEntry",
    "LeaderboardRotation",
    "Leaderboard",
)


class LeaderboardEntry(BaseModel):
    """Represents a character in the Tibiadrome leaderboards."""

    name: Optional[str] = None
    """The name of the character in the leaderboard. If ``None``, the character has been deleted."""
    rank: int
    """The rank of this entry."""
    drome_level: int
    """The Tibia Drome level of this entry."""

    @property
    def url(self) -> Optional[str]:
        """The URL of the character, if available."""
        return get_character_url(self.name) if self.name else None


class LeaderboardRotation(BaseModel):
    """A Tibiadrome leaderboards rotation."""

    rotation_id: int
    """The internal ID of the rotation."""
    is_current: bool
    """Whether this is the currently running rotation or not."""
    end_date: datetime.datetime
    """The date and time when this rotation ends."""

    def __eq__(self, other: Any):
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
    last_updated: Optional[datetime.datetime] = None
    """The time when the shown leaderboards were last updated. The resolution is 1 minute.

    Only available for the latest resolution.
    """

    @property
    def url(self) -> str:
        """The URL to the current leaderboard."""
        return get_leaderboards_url(self.world, self.rotation.rotation_id, self.current_page)

    def get_page_url(self, page: int) -> str:
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
