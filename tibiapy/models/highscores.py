import datetime
from typing import List, Optional, Set

from pydantic import BaseModel

from tibiapy import Category, VocationFilter, BattlEyeHighscoresFilter, PvpTypeFilter, Vocation
from tibiapy.models.base import BaseCharacter
from tibiapy.models.pagination import PaginatedWithUrl
from tibiapy.utils import get_tibia_url


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
    def from_rank(self):
        """:class:`int`: The starting rank of the provided entries."""
        return self.entries[0].rank if self.entries else 0

    @property
    def to_rank(self):
        """:class:`int`: The last rank of the provided entries."""
        return self.entries[-1].rank if self.entries else 0

    @property
    def url(self):
        """:class:`str`: The URL to the highscores page on Tibia.com containing the results."""
        return self.get_url(self.world, self.category, self.vocation, self.current_page, self.battleye_filter,
                            self.pvp_types_filter)

    def get_page_url(self, page):
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
        return self.get_url(self.world, self.category, self.vocation, page, self.battleye_filter, self.pvp_types_filter)

    @classmethod
    def get_url(cls, world=None, category=Category.EXPERIENCE, vocation=VocationFilter.ALL, page=1,
                battleye_type=None, pvp_types=None):
        """Get the Tibia.com URL of the highscores for the given parameters.
        Parameters
        ----------
        world: :class:`str`, optional
            The game world of the desired highscores. If no world is passed, ALL worlds are shown.
        category: :class:`Category`
            The desired highscores category.
        vocation: :class:`VocationFilter`
            The vocation filter to apply. By default all vocations will be shown.
        page: :class:`int`
            The page of highscores to show.
        battleye_type: :class:`BattlEyeHighscoresFilter`, optional
            The battleEye filters to use.
        pvp_types: :class:`list` of :class:`PvpTypeFilter`, optional
            The list of PvP types to filter the results for.
        Returns
        -------
        The URL to the Tibia.com highscores.
        """
        pvp_types = pvp_types or []
        pvp_params = [("worldtypes[]", p.value) for p in pvp_types]
        return get_tibia_url("community", "highscores", *pvp_params, world=world, category=category.value,
                             profession=vocation.value, currentpage=page,
                             beprotection=battleye_type.value if battleye_type else None)

