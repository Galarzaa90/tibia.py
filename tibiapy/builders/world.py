from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from tibiapy.enums import TransferType, BattlEyeType
from tibiapy.models import World, WorldEntry, WorldOverview

if TYPE_CHECKING:
    from tibiapy.models import OnlineCharacter
    from tibiapy.enums import WorldLocation, PvpType
    from typing_extensions import Self
    import datetime

__all__ = (
    "WorldBuilder",
    "WorldEntryBuilder",
    "WorldOverviewBuilder",
)


class WorldEntryBuilder:
    def __init__(self):
        self._name = None
        self._is_online = None
        self._location = None
        self._pvp_type = None
        self._online_count = 0
        self._transfer_type = TransferType.REGULAR
        self._battleye_since = None
        self._battleye_type = BattlEyeType.UNPROTECTED
        self._is_experimental = False
        self._is_premium_only = False

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def is_online(self, is_online: bool) -> Self:
        self._is_online = is_online
        return self

    def online_count(self, online_count: int) -> Self:
        self._online_count = online_count
        return self

    def location(self, location: WorldLocation) -> Self:
        self._location = location
        return self

    def pvp_type(self, pvp_type: PvpType) -> Self:
        self._pvp_type = pvp_type
        return self

    def is_premium_only(self, is_premium_only: bool) -> Self:
        self._is_premium_only = is_premium_only
        return self

    def transfer_type(self, transfer_type: TransferType) -> Self:
        self._transfer_type = transfer_type
        return self

    def battleye_since(self, battleye_since: Optional[datetime.datetime]) -> Self:
        self._battleye_since = battleye_since
        return self

    def battleye_type(self, battleye_type: BattlEyeType) -> Self:
        self._battleye_type = battleye_type
        return self

    def is_experimental(self, is_experimental: bool) -> Self:
        self._is_experimental = is_experimental
        return self

    def build(self) -> WorldEntry:
        return WorldEntry(
            name=self._name,
            is_online=self._is_online,
            online_count=self._online_count,
            location=self._location,
            pvp_type=self._pvp_type,
            is_premium_only=self._is_premium_only,
            transfer_type=self._transfer_type,
            battleye_since=self._battleye_since,
            battleye_type=self._battleye_type,
            is_experimental=self._is_experimental,
        )


class WorldBuilder(WorldEntryBuilder):
    def __init__(self):
        super().__init__()
        self._record_count = None
        self._record_date = None
        self._creation_date = None
        self._online_players = []
        self._world_quest_titles = []

    def record_count(self, record_count: int) -> Self:
        self._record_count = record_count
        return self

    def record_date(self, record_date: datetime.datetime) -> Self:
        self._record_date = record_date
        return self

    def creation_date(self, creation_date: str) -> Self:
        self._creation_date = creation_date
        return self

    def world_quest_titles(self, world_quest_titles: List[str]) -> Self:
        self._world_quest_titles = world_quest_titles
        return self

    def add_world_quest_title(self, world_quest_title: str) -> Self:
        self._world_quest_titles.append(world_quest_title)
        return self

    def online_players(self, online_players: List[OnlineCharacter]) -> Self:
        self._online_players = online_players
        return self

    def add_online_player(self, player: OnlineCharacter) -> Self:
        self._online_players.append(player)
        return self

    def build(self) -> World:
        return World(
            name=self._name,
            is_online=self._is_online,
            online_count=self._online_count,
            record_count=self._record_count,
            record_date=self._record_date,
            creation_date=self._creation_date,
            location=self._location,
            pvp_type=self._pvp_type,
            is_premium_only=self._is_premium_only,
            transfer_type=self._transfer_type,
            world_quest_titles=self._world_quest_titles,
            battleye_since=self._battleye_since,
            battleye_type=self._battleye_type,
            is_experimental=self._is_experimental,
            online_players=self._online_players,
        )


class WorldOverviewBuilder:
    def __init__(self) -> None:
        self._record_count = None
        self._record_date = None
        self._worlds = []

    def record_count(self, record_count: int) -> Self:
        self._record_count = record_count
        return self

    def record_date(self, record_date: datetime.datetime) -> Self:
        self._record_date = record_date
        return self

    def worlds(self, worlds: List[WorldEntry]) -> Self:
        self._worlds = worlds
        return self

    def build(self) -> WorldOverview:
        return WorldOverview(
            record_count=self._record_count,
            record_date=self._record_date,
            worlds=self._worlds,
        )
