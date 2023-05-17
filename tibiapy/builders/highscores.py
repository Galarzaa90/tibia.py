from __future__ import annotations

import datetime
from typing import List, TYPE_CHECKING

from tibiapy.models import Highscores

if TYPE_CHECKING:
    from tibiapy import HighscoresCategory, HighscoresProfession, HighscoresBattlEyeType, PvpTypeFilter
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

    def world(self, world: str):
        self._world = world
        return self

    def category(self, category: HighscoresCategory):
        self._category = category
        return self

    def vocation(self, vocation: HighscoresProfession):
        self._vocation = vocation
        return self

    def battleye_filter(self, battleye_filter: HighscoresBattlEyeType):
        self._battleye_filter = battleye_filter
        return self

    def pvp_types_filter(self, pvp_types_filter: PvpTypeFilter):
        self._pvp_types_filter = pvp_types_filter
        return self

    def current_page(self, current_page: int):
        self._current_page = current_page
        return self

    def total_pages(self, total_pages: int):
        self._total_pages = total_pages
        return self

    def results_count(self, results_count: int):
        self._results_count = results_count
        return self

    def last_updated(self, last_updated: datetime.datetime):
        self._last_updated = last_updated
        return self

    def entries(self, entries: List[HighscoresEntry]):
        self._entries = entries
        return self

    def add_entry(self, entry: HighscoresEntry):
        self._entries.append(entry)
        return self

    def available_worlds(self, available_worlds: List[str]):
        self._available_worlds = available_worlds
        return self

    def build(self):
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
