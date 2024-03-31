from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from tibiapy.models.leaderboard import LeaderboardEntry, Leaderboard

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from tibiapy.models.leaderboard import LeaderboardRotation


class LeaderboardBuilder:
    def __init__(self):
        self._world = None
        self._available_worlds = None
        self._rotation = None
        self._available_rotations = None
        self._entries = []
        self._last_updated = None
        self._current_page = None
        self._total_pages = None
        self._results_count = None

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def available_worlds(self, available_worlds: List[str]) -> Self:
        self._available_worlds = available_worlds
        return self

    def rotation(self, rotation: LeaderboardRotation) -> Self:
        self._rotation = rotation
        return self

    def available_rotations(self, available_rotations: List[LeaderboardRotation]) -> Self:
        self._available_rotations = available_rotations
        return self

    def entries(self, entries: List[LeaderboardEntry]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry: LeaderboardEntry) -> Self:
        self._entries.append(entry)
        return self

    def last_updated(self, last_updated: Optional[datetime.datetime]) -> Self:
        self._last_updated = last_updated
        return self

    def current_page(self, current_page: int) -> Self:
        self._current_page = current_page
        return self

    def total_pages(self, total_pages: int) -> Self:
        self._total_pages = total_pages
        return self

    def results_count(self, results_count: int) -> Self:
        self._results_count = results_count
        return self

    def build(self) -> Leaderboard:
        return Leaderboard(
            world=self._world,
            available_worlds=self._available_worlds,
            rotation=self._rotation,
            available_rotations=self._available_rotations,
            entries=self._entries,
            last_updated=self._last_updated,
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
        )


class LeaderboardEntryBuilder:

    def __init__(self):
        self._name = None
        self._rank = None
        self._drome_level = None

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def rank(self, rank: int) -> Self:
        self._rank = rank
        return self

    def drome_level(self, drome_level: int) -> Self:
        self._drome_level = drome_level
        return self

    def build(self) -> LeaderboardEntry:
        return LeaderboardEntry(
            name=self._name,
            rank=self._rank,
            drome_level=self._drome_level,
        )
