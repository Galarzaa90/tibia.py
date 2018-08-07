class Death:
    """
    Represents a death by a character

    Attributes
    -----------
    name: :class:`str`
        The name of the character this death belongs to.

    level: :class:`int`
        The level at which the level occurred.

    killer: :class:`str`
        The main killer.

    time: :class:`str`
        The time at which the death occurred.

    by_player: :class:`bool`
        True if the killer is a player, False otherwise.

    participants: :class:`list`
        List of all participants in the death.
    """
    __slots__ = ("name", "level", "killer", "time", "by_player", "participants")

    def __init__(self, level, killer, time, by_player, **kwargs):
        self.level = level
        self.killer = killer
        self.time = time
        self.by_player = by_player
        self.participants = kwargs.get("participants", [])
        self.name = kwargs.get("name")