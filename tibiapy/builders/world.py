import datetime
from typing import List, Optional

from tibiapy import WorldLocation, PvpType, TransferType, BattlEyeType, TournamentWorldType
from tibiapy.models import OnlineCharacter
from tibiapy.models.world import World, WorldEntry, WorldOverview
from tibiapy.utils import try_enum, try_datetime, try_date


__all__ = (
    "WorldBuilder",
    "WorldEntryBuilder",
    "WorldOverviewBuilder"
)


class WorldBuilder:
    def __init__(self, **kwargs):
        self._name: str = kwargs.get("name")
        self._online = kwargs.get("online", False)
        self._location = try_enum(WorldLocation, kwargs.get("location"))
        self._pvp_type = try_enum(PvpType, kwargs.get("pvp_type"))
        self._online_count: int = kwargs.get("online_count", 0)
        self._record_count: int = kwargs.get("record_count", 0)
        self._record_date = try_datetime(kwargs.get("record_date"))
        self._creation_date: str = kwargs.get("creation_date")
        self._transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self._world_quest_titles: List[str] = kwargs.get("world_quest_titles", [])
        self._battleye_date = try_date(kwargs.get("battleye_date"))
        self._battleye_type = try_enum(BattlEyeType, kwargs.get("battleye_type"), BattlEyeType.UNPROTECTED)
        self._experimental: bool = kwargs.get("experimental", False)
        self._online_players: List[OnlineCharacter] = kwargs.get("online_players", [])
        self._premium_only: bool = kwargs.get("premium_only", False)
        self._tournament_world_type = try_enum(TournamentWorldType, kwargs.get("tournament_world_type"), None)

    def name(self, name: str) -> 'WorldBuilder':
        self._name = name
        return self

    def online(self, online: bool) -> 'WorldBuilder':
        self._online = online
        return self

    def online_count(self, online_count: int) -> 'WorldBuilder':
        self._online_count = online_count
        return self

    def record_count(self, record_count: int) -> 'WorldBuilder':
        self._record_count = record_count
        return self

    def record_date(self, record_date: datetime.datetime) -> 'WorldBuilder':
        self._record_date = record_date
        return self

    def creation_date(self, creation_date: str) -> 'WorldBuilder':
        self._creation_date = creation_date
        return self

    def location(self, location: WorldLocation) -> 'WorldBuilder':
        self._location = location
        return self

    def pvp_type(self, pvp_type: PvpType) -> 'WorldBuilder':
        self._pvp_type = pvp_type
        return self

    def premium_only(self, premium_only: bool) -> 'WorldBuilder':
        self._premium_only = premium_only
        return self

    def transfer_type(self, transfer_type: TransferType) -> 'WorldBuilder':
        self._transfer_type = transfer_type
        return self

    def world_quest_titles(self, world_quest_titles: List[str]) -> 'WorldBuilder':
        self._world_quest_titles = world_quest_titles
        return self

    def add_world_quest_title(self, world_quest_title: str) -> 'WorldBuilder':
        self._world_quest_titles.append(world_quest_title)
        return self

    def battleye_date(self, battleye_date: Optional[datetime.datetime]) -> 'WorldBuilder':
        self._battleye_date = battleye_date
        return self

    def battleye_type(self, battleye_type: BattlEyeType) -> 'WorldBuilder':
        self._battleye_type = battleye_type
        return self

    def experimental(self, experimental: bool) -> 'WorldBuilder':
        self._experimental = experimental
        return self

    def online_players(self, online_players: List[OnlineCharacter]) -> 'WorldBuilder':
        self._online_players = online_players
        return self

    def add_online_player(self, player: OnlineCharacter) -> 'WorldBuilder':
        self._online_players.append(player)
        return self

    def build(self):
        return World(
            name=self._name,
            online=self._online,
            online_count=self._online_count,
            record_count=self._record_count,
            record_date=self._record_date,
            creation_date=self._creation_date,
            location=self._location,
            pvp_type=self._pvp_type,
            premium_only=self._premium_only,
            transfer_type=self._transfer_type,
            world_quest_titles=self._world_quest_titles,
            battleye_date=self._battleye_date,
            battleye_type=self._battleye_type,
            experimental=self._experimental,
            online_players=self._online_players,
        )
    

class WorldEntryBuilder:
    def __init__(self, **kwargs):
        self._name: str = kwargs.get("name")
        self._online = kwargs.get("online", False)
        self._location = try_enum(WorldLocation, kwargs.get("location"))
        self._pvp_type = try_enum(PvpType, kwargs.get("pvp_type"))
        self._online_count: int = kwargs.get("online_count", 0)
        self._transfer_type = try_enum(TransferType, kwargs.get("transfer_type", TransferType.REGULAR))
        self._battleye_date = try_date(kwargs.get("battleye_date"))
        self._battleye_type = try_enum(BattlEyeType, kwargs.get("battleye_type"), BattlEyeType.UNPROTECTED)
        self._experimental: bool = kwargs.get("experimental", False)
        self._premium_only: bool = kwargs.get("premium_only", False)

    def name(self, name: str) -> 'WorldEntryBuilder':
        self._name = name
        return self

    def online(self, online: bool) -> 'WorldEntryBuilder':
        self._online = online
        return self

    def online_count(self, online_count: int) -> 'WorldEntryBuilder':
        self._online_count = online_count
        return self

    def location(self, location: WorldLocation) -> 'WorldEntryBuilder':
        self._location = location
        return self

    def pvp_type(self, pvp_type: PvpType) -> 'WorldEntryBuilder':
        self._pvp_type = pvp_type
        return self

    def premium_only(self, premium_only: bool) -> 'WorldEntryBuilder':
        self._premium_only = premium_only
        return self

    def transfer_type(self, transfer_type: TransferType) -> 'WorldEntryBuilder':
        self._transfer_type = transfer_type
        return self

    def world_quest_titles(self, world_quest_titles: List[str]) -> 'WorldEntryBuilder':
        self._world_quest_titles = world_quest_titles
        return self

    def add_world_quest_title(self, world_quest_title: str) -> 'WorldEntryBuilder':
        self._world_quest_titles.append(world_quest_title)
        return self

    def battleye_date(self, battleye_date: Optional[datetime.datetime]) -> 'WorldEntryBuilder':
        self._battleye_date = battleye_date
        return self

    def battleye_type(self, battleye_type: BattlEyeType) -> 'WorldEntryBuilder':
        self._battleye_type = battleye_type
        return self

    def experimental(self, experimental: bool) -> 'WorldEntryBuilder':
        self._experimental = experimental
        return self

    def build(self):
        return WorldEntry(
            name=self._name,
            online=self._online,
            online_count=self._online_count,
            location=self._location,
            pvp_type=self._pvp_type,
            premium_only=self._premium_only,
            transfer_type=self._transfer_type,
            battleye_date=self._battleye_date,
            battleye_type=self._battleye_type,
            experimental=self._experimental,
        )
    
class WorldOverviewBuilder:
    def __init__(self, **kwargs) -> None:
        self._record_count = kwargs.get("record_count")
        self._record_date = kwargs.get("record_date")
        self._worlds = kwargs.get("worlds")

    def record_count(self, record_count: int) -> 'WorldOverviewBuilder':
        self._record_count = record_count
        return self
    
    def record_date(self, record_date: datetime.datetime) -> 'WorldOverviewBuilder':
        self._record_date = record_date
        return self
    
    def worlds(self, worlds: List[WorldEntry]) -> 'WorldOverviewBuilder':
        self._worlds = worlds
        return self

    def build(self):
        return WorldOverview(
            record_count=self._record_count,
            record_date=self._record_date,
            worlds=self._worlds,
        )