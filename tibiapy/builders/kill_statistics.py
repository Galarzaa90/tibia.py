from typing import List

from tibiapy.models import RaceEntry, KillStatistics


class KillStatisticsBuilder:
    def __init__(self, **kwargs):
        self._world = kwargs.get("world")
        self._entries = kwargs.get("entries") or {}
        self._total = kwargs.get("total")
        self._available_worlds = kwargs.get("available_worlds")

    def world(self, world: str) -> 'KillStatisticsBuilder':
        self._world = world
        return self

    def entries(self, entries: List[RaceEntry]) -> 'KillStatisticsBuilder':
        self._entries = entries
        return self

    def set_entry(self, name: str, entry: RaceEntry) -> 'KillStatisticsBuilder':
        self._entries[name] = entry
        return self

    def total(self, total: RaceEntry) -> 'KillStatisticsBuilder':
        self._total = total
        return self

    def available_worlds(self, available_worlds: List[str]) -> 'KillStatisticsBuilder':
        self._available_worlds = available_worlds
        return self

    def build(self):
        return KillStatistics(
            world=self._world,
            entries=self._entries,
            total=self._total,
            available_worlds=self._available_worlds
        )

