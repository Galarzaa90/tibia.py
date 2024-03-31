"""Models related to game worlds."""
import datetime
from typing import List, Optional

from pydantic import computed_field

from tibiapy.enums import BattlEyeType, PvpType, TransferType, WorldLocation
from tibiapy.models import OnlineCharacter
from tibiapy.models.base import BaseModel
from tibiapy.urls import get_world_url

__all__ = (
    "BaseWorld",
    "World",
    "WorldEntry",
    "WorldOverview",
)


class BaseWorld(BaseModel):
    """Base class for all World classes."""

    name: str
    """The name of the world."""
    is_online: bool
    """Whether the world is online or not."""
    online_count: int
    """The number of currently online players in the world."""
    location: WorldLocation
    """The physical location of the game servers."""
    pvp_type: PvpType
    """The type of PvP in the world."""
    transfer_type: TransferType
    """The type of transfer restrictions this world has."""
    is_premium_only: bool
    """Whether only premium account players are allowed to play in this server."""
    battleye_since: Optional[datetime.date] = None
    """The date when BattlEye was added to this world."""
    battleye_type: BattlEyeType
    """The type of BattlEye protection this world has."""
    is_experimental: bool
    """Whether the world is experimental or not."""

    @property
    def url(self) -> str:
        """URL to the world's information page on Tibia.com."""
        return get_world_url(self.name)

    @computed_field
    @property
    def is_battleye_protected(self) -> bool:
        """Whether the server is currently protected with BattlEye or not.

        .. versionchanged:: 4.0.0
            Now a calculated property instead of a field.
        """
        return self.battleye_type and self.battleye_type != BattlEyeType.UNPROTECTED


class World(BaseWorld):
    """Represents a Tibia game server."""

    record_count: int
    """The server's online players record."""
    record_date: datetime.datetime
    """The date when the online record was achieved."""
    creation_date: str
    """The month and year the world was created. In YYYY-MM format."""
    world_quest_titles: List[str]
    """List of world quest titles the server has achieved."""
    online_players: List[OnlineCharacter]
    """A list of characters currently online in the server."""

    @property
    def creation_year(self) -> int:
        """Returns the year when the world was created."""
        return int(self.creation_date.split("-")[0]) if self.creation_date else None

    @property
    def creation_month(self) -> int:
        """Returns the month when the world was created."""
        return int(self.creation_date.split("-")[1]) if self.creation_date else None


class WorldEntry(BaseWorld):
    """Represents a game server listed in the World Overview section."""


class WorldOverview(BaseModel):
    """Container class for the World Overview section."""

    record_count: int
    """The overall player online record."""
    record_date: datetime.datetime
    """The date when the record was achieved."""
    worlds: List[WorldEntry] = []
    """List of worlds, with limited info."""

    @computed_field
    @property
    def total_online(self) -> int:
        """Total players online across all worlds."""
        return sum(w.online_count for w in self.worlds)
