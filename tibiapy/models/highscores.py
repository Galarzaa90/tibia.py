import datetime
from typing import List, Optional, Set

from tibiapy import Category, VocationFilter, BattlEyeHighscoresFilter, PvpTypeFilter, Vocation
from tibiapy.models.base import BaseCharacter
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.urls import get_highscores_url


class HighscoresEntry(BaseCharacter):
    """Represents an entry for the highscores."""

    name: str
    """The name of the character."""
    rank: int
    """The character's rank in the respective highscores."""
    vocation: Vocation
    """The character's vocation."""
    world: str
    """The character's world."""
    level: int
    """The character's level."""
    value: int
    """The character's value for the highscores."""


class LoyaltyHighscoresEntry(HighscoresEntry):
    """Represents an entry for the highscores loyalty points category.

    This is a subclass of :class:`HighscoresEntry`, adding an extra field for title."""

    title: str
    """The character's loyalty title."""


class Highscores(PaginatedWithUrl[HighscoresEntry]):
    """Represents the highscores of a world."""

    world:  Optional[str] = None
    """The world the highscores belong to. If this is :obj:`None`, the highscores shown are for all worlds."""
    category: Category
    """The selected category to displays the highscores of."""
    vocation: VocationFilter
    """The selected vocation to filter out values."""
    battleye_filter: Optional[BattlEyeHighscoresFilter]
    """The selected BattlEye filter. If :obj:`None`, all worlds will be displayed.

    Only applies for global highscores. Only characters from worlds with the matching BattlEye protection will be shown."""
    pvp_types_filter: Set[PvpTypeFilter]
    """The selected PvP types filter. If :obj:`None`, all world will be displayed.

    Only applies for global highscores. Only characters from worlds with the matching PvP type will be shown."""
    last_updated: datetime.timedelta
    """How long ago were this results updated. The resolution is 1 minute."""
    available_worlds: List[str]
    """The worlds available for selection."""



    @property
    def from_rank(self) -> int:
        """The starting rank of the provided entries."""
        return self.entries[0].rank if self.entries else 0

    @property
    def to_rank(self) -> int:
        """The last rank of the provided entries."""
        return self.entries[-1].rank if self.entries else 0

    @property
    def url(self) -> str:
        """The URL to the highscores page on Tibia.com containing the results."""
        return get_highscores_url(self.world, self.category, self.vocation, self.current_page, self.battleye_filter,
                            self.pvp_types_filter)

    def get_page_url(self, page: int) -> str:
        """Get the URL to a specific page for the current highscores.

        Parameters
        ----------
        page: :class:`int`
            The page to get the URL for.

        Returns
        -------
        :class:`str`
            The URL to the page of the current highscores.

        Raises
        ------
        ValueError
            The provided page is less or equals than zero.
        """
        if page <= 0:
            raise ValueError("page cannot be less or equals than zero")
        return get_highscores_url(self.world, self.category, self.vocation, page, self.battleye_filter, self.pvp_types_filter)

