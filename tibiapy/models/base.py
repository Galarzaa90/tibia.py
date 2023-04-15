"""Base classes shared by various models."""
from __future__ import annotations

from pydantic import BaseModel

from tibiapy.utils import get_tibia_url


class BaseCharacter(BaseModel):
    name: str

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    @property
    def url(self):
        """:class:`str`: The URL of the character's information page on Tibia.com."""
        return self.get_url(self.name)

    @classmethod
    def get_url(cls, name):
        """Get the Tibia.com URL for a given character name.

        Parameters
        ------------
        name: :class:`str`
            The name of the character.

        Returns
        --------
        :class:`str`
            The URL to the character's page.
        """
        return get_tibia_url("community", "characters", name=name)


class BaseGuild(BaseModel):
    """Base class for Guild classes."""

    name: str
    """The name of the guild."""

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the guild's information page on Tibia.com."""
        return self.get_url(self.name)

    @property
    def url_wars(self):
        """:class:`str` The URL to the guild's wars page on Tibia.com.

        .. versionadded:: 3.0.0
        """
        return self.get_url_wars(self.name)

    @classmethod
    def get_url(cls, name):
        """Get the Tibia.com URL for a given guild name.

        Parameters
        ------------
        name: :class:`str`
            The name of the guild.

        Returns
        --------
        :class:`str`
            The URL to the guild's page.
        """
        return get_tibia_url("community", "guilds", page="view", GuildName=name)

    @classmethod
    def get_url_wars(cls, name):
        """Get the Tibia.com URL for the guild wars of a guild with a given name.

        .. versionadded:: 3.0.0

        Parameters
        ------------
        name: :class:`str`
            The name of the guild.

        Returns
        --------
        :class:`str`
            The URL to the guild's wars page.
        """
        return get_tibia_url("community", "guilds", page="guildwars", action="view", GuildName=name)


class BaseHouse(BaseModel):
    """Base class for all house classes.

    The following implement this class:

    - :class:`.House`
    - :class:`.GuildHouse`
    - :class:`.CharacterHouse`
    - :class:`.HouseEntry`
    """

    name: str
    """The name of the house."""

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()
        return False

    @classmethod
    def get_url(cls, house_id, world):
        """Get the Tibia.com URL for a house with the given id and world.

        Parameters
        ----------
        house_id: :class:`int`
            The internal id of the house.
        world: :class:`str`
            The world of the house.

        Returns
        -------
        The URL to the house in Tibia.com
        """
        return get_tibia_url("community", "houses", page="view", houseid=house_id, world=world)


class HouseWithId(BaseHouse):
    id: int
    """The internal ID of the house. This is used on the website to identify houses."""
    world: str
    """The name of the world the house belongs to."""

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names or ids are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower() or self.id == o.id
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the house."""
        return self.get_url(self.id, self.world) if self.id and self.world else None
