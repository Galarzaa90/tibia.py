from tibiapy.models import Highscores


class HighscoresBuilder:

    def __init__(self, **kwargs):
        self._world = kwargs.get("world")
        self._category = kwargs.get("category")
        self._vocation = kwargs.get("vocation")
        self._battleye_filter = kwargs.get("battleye_filter")
        self._pvp_types_filter = kwargs.get("pvp_types_filter")
        self._current_page = kwargs.get("current_page")
        self._total_pages = kwargs.get("total_pages")
        self._results_count = kwargs.get("results_count")
        self._last_updated = kwargs.get("last_updated")
        self._entries = kwargs.get("entries") or []
        self._available_worlds = kwargs.get("available_worlds")

    def world(self, world) -> 'HighscoresBuilder':
        self._world = world
        return self

    def category(self, category) -> 'HighscoresBuilder':
        self._category = category
        return self

    def vocation(self, vocation) -> 'HighscoresBuilder':
        self._vocation = vocation
        return self

    def battleye_filter(self, battleye_filter) -> 'HighscoresBuilder':
        self._battleye_filter = battleye_filter
        return self

    def pvp_types_filter(self, pvp_types_filter) -> 'HighscoresBuilder':
        self._pvp_types_filter = pvp_types_filter
        return self

    def current_page(self, current_page) -> 'HighscoresBuilder':
        self._current_page = current_page
        return self

    def total_pages(self, total_pages) -> 'HighscoresBuilder':
        self._total_pages = total_pages
        return self

    def results_count(self, results_count) -> 'HighscoresBuilder':
        self._results_count = results_count
        return self

    def last_updated(self, last_updated) -> 'HighscoresBuilder':
        self._last_updated = last_updated
        return self


    def entries(self, entries) -> 'HighscoresBuilder':
        self._entries = entries
        return self

    def add_entry(self, entry) -> 'HighscoresBuilder':
        self._entries.append(entry)
        return self

    def available_worlds(self, available_worlds) -> 'HighscoresBuilder':
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
