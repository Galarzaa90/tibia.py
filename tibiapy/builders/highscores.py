from __future__ import annotations

from typing import List, Set, TYPE_CHECKING

from tibiapy.models import Highscores

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from tibiapy.enums import HighscoresCategory, HighscoresProfession, HighscoresBattlEyeType, PvpTypeFilter
    from tibiapy.models import HighscoresEntry


class HighscoresBuilder:

    def __init__(self):
        self._world = None
        self._category = None
        self._vocation = None
        self._battleye_filter = None
        self._pvp_types_filter = None
        self._current_page = None
        self._total_pages = None
        self._results_count = None
        self._last_updated = None
        self._entries = []
        self._available_worlds = None

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def category(self, category: HighscoresCategory) -> Self:
        self._category = category
        return self

    def vocation(self, vocation: HighscoresProfession) -> Self:
        self._vocation = vocation
        return self

    def battleye_filter(self, battleye_filter: HighscoresBattlEyeType) -> Self:
        self._battleye_filter = battleye_filter
        return self

    def pvp_types_filter(self, pvp_types_filter: Set[PvpTypeFilter]) -> Self:
        self._pvp_types_filter = pvp_types_filter
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

    def last_updated(self, last_updated: datetime.datetime) -> Self:
        self._last_updated = last_updated
        return self

    def entries(self, entries: List[HighscoresEntry]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry: HighscoresEntry) -> Self:
        self._entries.append(entry)
        return self

    def available_worlds(self, available_worlds: List[str]) -> Self:
        self._available_worlds = available_worlds
        return self

    def build(self) -> Highscores:
        return Highscores(
            world=self._world,
            category=self._category,
            vocation=self._vocation,
            battleye_filter=self._battleye_filter,
            pvp_types_filter=self._pvp_types_filter,
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
            last_updated=self._last_updated,
            entries=self._entries,
            available_worlds=self._available_worlds,
        )
