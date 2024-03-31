from __future__ import annotations

from typing import List, TYPE_CHECKING

from tibiapy.models import KillStatistics

if TYPE_CHECKING:
    from typing_extensions import Self
    from tibiapy.models import RaceEntry


class KillStatisticsBuilder:
    def __init__(self):
        self._world = None
        self._entries = {}
        self._total = None
        self._available_worlds = None

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def entries(self, entries: List[RaceEntry]) -> Self:
        self._entries = entries
        return self

    def set_entry(self, name: str, entry: RaceEntry) -> Self:
        self._entries[name] = entry
        return self

    def total(self, total: RaceEntry) -> Self:
        self._total = total
        return self

    def available_worlds(self, available_worlds: List[str]) -> Self:
        self._available_worlds = available_worlds
        return self

    def build(self) -> KillStatistics:
        return KillStatistics(
            world=self._world,
            entries=self._entries,
            total=self._total,
            available_worlds=self._available_worlds,
        )
