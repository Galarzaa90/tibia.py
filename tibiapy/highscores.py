from tibiapy import abc


class Highscores(abc.Serializable):
    def __init__(self, world, category, **kwargs):
        self.world = world
        self.category = category
        self.vocation = kwargs.get("vocation", "all")
        self.entries = kwargs.get("entries", [])
        self.results_count = kwargs.get("results_count")


class HighscoresEntry(abc.BaseCharacter):
    def __init__(self, name, rank, vocation, value, extra=None):
        self.name = name
        self.rank = rank
        self.vocation = vocation
        self.value = value
        self.extra = extra
