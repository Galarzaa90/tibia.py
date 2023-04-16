from typing import List, Optional

from pydantic import BaseModel

from tibiapy.utils import get_tibia_url


class BossEntry(BaseModel):
    """Represents a boss in the boostable bosses section in the Tibia.com library."""

    name: str
    """The name of the boss."""
    identifier: str
    """The internal name of the boss. Used for images."""

    @property
    def image_url(self):
        """:class:`str`: The URL to this boss's image."""
        return f"https://static.tibia.com/images/library/{self.identifier}.gif"


class BoostableBosses(BaseModel):
    """Represents the boostable bosses section in the Tibia.com library"""

    boosted_boss: BossEntry
    """The current boosted boss."""
    bosses: List[BossEntry]
    """The list of boostable bosses."""

    @classmethod
    def get_url(cls):
        """Get the URL to the Tibia.com boostable bosses.

        Returns
        -------
        :class:`str`:
            The URL to the Tibia.com library section.
        """
        return get_tibia_url("library", "boostablebosses")


class CreatureEntry(BaseModel):
    """Represents a creature in the Library section."""

    name: str
    """The name of the creature, usually in plural, except for the boosted creature."""
    identifier: str
    """The internal name of the creature's race. Used for links and images."""

    @property
    def url(self):
        """:class:`str`: The URL to this creature's details."""
        return self.get_url(self.identifier)

    @property
    def image_url(self):
        """:class:`str`: The URL to this creature's image."""
        return f"https://static.tibia.com/images/library/{self.identifier}.gif"

    @classmethod
    def get_url(cls, identifier):
        """Get the URL to the creature's detail page on Tibia.com.

        Parameters
        ----------
        identifier: :class:`str`
            The race's internal name.

        Returns
        -------
        :class:`str`
            The URL to the detail page.
        """
        return get_tibia_url("library", "creatures", race=identifier)


class Creature(CreatureEntry):
    """Represents a creature's details on the Tibia.com library."""

    name: str
    """The name of the creature, in plural form."""
    identifier: str
    """The race's internal name. Used for links and images."""
    description: str
    """A description of the creature."""
    hitpoints: int
    """The number of hitpoints the creature has."""
    experience: int
    """The number of experience points given for killing this creature."""
    immune_to: List[str]
    """The elements this creature is immune to."""
    weak_against: List[str]
    """The elements this creature is weak against."""
    strong_against: List[str]
    """The elements this creature is strong against."""
    loot: str
    """Some of the items this creature drops."""
    mana_cost: Optional[int]
    """The mana neccessary to summon or convince this creature."""
    summonable: bool
    """Whether this creature can be summoned or not."""
    convinceable: bool
    """Whether this creature can be convinced or not."""


class CreaturesSection(BaseModel):
    """Represents the creature's section in the Tibia.com library."""

    boosted_creature: CreatureEntry
    """The current boosted creature."""
    creatures: List[CreatureEntry]
    """The list of creatures in the library."""

    @classmethod
    def get_url(cls):
        """Get the URL to the Tibia.com library section.

        Returns
        -------
        :class:`str`:
            The URL to the Tibia.com library section.
        """
        return get_tibia_url("library", "creature")


class BoostedCreatures(BaseModel):
    """Contains both boosted creature and boosted boss."""

    creature: CreatureEntry
    """The boosted creature of the day."""
    boss: BossEntry
    """The boosted boss of the day."""
