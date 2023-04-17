import datetime
from typing import List, Optional

from tibiapy import WorldLocation, PvpType, TransferType, BattlEyeType
from tibiapy.models import OnlineCharacter, BaseModel
from tibiapy.urls import get_world_url


class BaseWorld(BaseModel):
    """Base class for all World classes."""
    name: str
    """The name of the world."""

    @property
    def url(self) -> str:
        """URL to the world's information page on Tibia.com."""
        return get_world_url(self.name)


class World(BaseWorld):
    """Represents a Tibia game server."""
    online: bool
    """Whether the world is online or not."""
    online_count: int
    """The number of currently online players in the world."""
    record_count: int
    """The server's online players record."""
    record_date: datetime.datetime
    """The date when the online record was achieved."""
    creation_date: str
    """The month and year the world was created. In YYYY-MM format."""
    location: WorldLocation
    """The physical location of the game servers."""
    pvp_type: PvpType
    """The type of PvP in the world."""
    premium_only: bool
    """Whether only premium account players are allowed to play in this server."""
    transfer_type: TransferType
    """The type of transfer restrictions this world has."""
    world_quest_titles: List[str]
    """List of world quest titles the server has achieved."""
    battleye_date: Optional[datetime.date]
    """The date when BattlEye was added to this world."""
    battleye_type: BattlEyeType = BattlEyeType.UNPROTECTED
    """The type of BattlEye protection this world has."""
    experimental: bool = False
    """Whether the world is experimental or not."""
    online_players: List[OnlineCharacter]
    """A list of characters currently online in the server."""

    @property
    def battleye_protected(self) -> bool:
        """Whether the server is currently protected with BattlEye or not.

        .. versionchanged:: 4.0.0
            Now a calculated property instead of a field.
        """
        return self.battleye_type and self.battleye_type != BattlEyeType.UNPROTECTED

    @property
    def creation_year(self) -> int:
        """Returns the year when the world was created."""
        return int(self.creation_date.split("-")[0]) if self.creation_date else None

    @property
    def creation_month(self) -> int:
        """Returns the month when the world was created."""
        return int(self.creation_date.split("-")[1]) if self.creation_date else None


class WorldEntry(BaseWorld):
    name: str
    """The name of the world."""
    online: bool
    """Whether the world is currently online."""
    online_count: int
    """The number of currently online players in the world."""
    location: WorldLocation
    """The physical location of the game servers."""
    pvp_type: PvpType
    """The type of PvP in the world."""
    transfer_type: TransferType
    """The type of transfer restrictions this world has."""
    battleye_date: Optional[datetime.date]
    """The date when BattlEye was added to this world."""
    battleye_type: BattlEyeType = BattlEyeType.UNPROTECTED
    """The type of BattlEye protection this world has."""
    experimental: bool = False
    """Whether the world is experimental or not."""
    premium_only: bool
    """Whether only premium account players are allowed to play in this server."""

    @property
    def battleye_protected(self) -> bool:
        """Whether the server is currently protected with BattlEye or not.

        .. versionchanged:: 4.0.0
            Now a calculated property instead of a field.
        """
        return self.battleye_type and self.battleye_type != BattlEyeType.UNPROTECTED


class WorldOverview(BaseModel):
    """Container class for the World Overview section."""

    record_count: int
    """The overall player online record."""
    record_date: datetime.datetime
    """The date when the record was achieved."""
    worlds: List[WorldEntry] = []
    """List of worlds, with limited info."""

    @property
    def total_online(self) -> int:
        """Total players online across all worlds."""
        return sum(w.online_count for w in self.worlds)
