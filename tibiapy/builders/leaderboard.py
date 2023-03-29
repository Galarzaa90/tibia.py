import datetime
from typing import List, Optional

from tibiapy.models.leaderboards import LeaderboardRotation, LeaderboardEntry, Leaderboard


class LeaderboardBuilder:
    def __init__(self, **kwargs):
        self._world = kwargs.get("world")
        self._available_worlds = kwargs.get("available_worlds")
        self._rotation = kwargs.get("rotation")
        self._available_rotations = kwargs.get("available_rotations")
        self._entries = kwargs.get("entries") or []
        self._last_update = kwargs.get("last_update")
        self._page = kwargs.get("page")
        self._total_pages = kwargs.get("total_pages")
        self._results_count = kwargs.get("results_count")

    def world(self, world: str) -> 'LeaderboardBuilder':
        self._world = world
        return self

    def available_worlds(self, available_worlds: List[str]) -> 'LeaderboardBuilder':
        self._available_worlds = available_worlds
        return self

    def rotation(self, rotation: LeaderboardRotation) -> 'LeaderboardBuilder':
        self._rotation = rotation
        return self

    def available_rotations(self, available_rotations: List[LeaderboardRotation]) -> 'LeaderboardBuilder':
        self._available_rotations = available_rotations
        return self

    def entries(self, entries: List[LeaderboardEntry]) -> 'LeaderboardBuilder':
        self._entries = entries
        return self

    def add_entry(self, entry: LeaderboardEntry) -> 'LeaderboardBuilder':
        self._entries.append(entry)
        return self

    def last_update(self, last_update: Optional[datetime.timedelta]) -> 'LeaderboardBuilder':
        self._last_update = last_update
        return self

    def page(self, page: int) -> 'LeaderboardBuilder':
        self._page = page
        return self

    def total_pages(self, total_pages: int) -> 'LeaderboardBuilder':
        self._total_pages = total_pages
        return self

    def results_count(self, results_count: int) -> 'LeaderboardBuilder':
        self._results_count = results_count
        return self

    def build(self):
        return Leaderboard(
            world=self._world,
            available_worlds=self._available_worlds,
            rotation=self._rotation,
            available_rotations=self._available_rotations,
            entries=self._entries,
            last_update=self._last_update,
            page=self._page,
            total_pages=self._total_pages,
            results_count=self._results_count,
        )


class LeaderboardEntryBuilder:

    def __init__(self, **kwargs):
        self._name = kwargs.get("name")
        self._rank = kwargs.get("rank")
        self._drome_level = kwargs.get("drome_level")

    def name(self, name: str) -> 'LeaderboardEntryBuilder':
        self._name = name
        return self

    def rank(self, rank: int) -> 'LeaderboardEntryBuilder':
        self._rank = rank
        return self

    def drome_level(self, drome_level: int) -> 'LeaderboardEntryBuilder':
        self._drome_level = drome_level
        return self

    def build(self):
        return LeaderboardEntryBuilder(
            name=self._name,
            rank=self._rank,
            drome_level=self._drome_level,
        )
