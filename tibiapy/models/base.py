"""Base classes shared by various models."""
from __future__ import annotations

from typing import Any

import pydantic
from pydantic import ConfigDict

import tibiapy

__all__ = (
    "BaseModel",
    "BaseCharacter",
    "BaseGuild",
    "BaseHouse",
    "HouseWithId",
)


def to_camel(string: str) -> str:
    string_split = string.split("_")
    return string_split[0] + "".join(word.capitalize() for word in string_split[1:])


class BaseModel(pydantic.BaseModel):
    """Base class for all model classes."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class BaseCharacter(BaseModel):
    """Base class for all character classes.

    The following implement this class:

    - :class:`.Character`
    - :class:`.GuildInvite`
    - :class:`.GuildMember`
    - :class:`.HighscoresEntry`
    - :class:`.TournamentLeaderboardEntry`
    - :class:`.OnlineCharacter`
    - :class:`.OtherCharacter`
    - :class:`.Auction`
    """

    name: str
    """The name of the character."""

    def __eq__(self, o: object) -> bool:
        """Two characters are considered equal if their names are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower()

        return False

    @property
    def url(self) -> str:
        """The URL of the character's information page on Tibia.com."""
        return tibiapy.urls.get_character_url(self.name)


class BaseGuild(BaseModel):
    """Base class for Guild classes.

    The following implement this class:

    - :class:`.Guild`
    - :class:`.GuildMembership`
    - :class:`.GuildEntry`
    """

    name: str
    """The name of the guild."""

    def __eq__(self, other: Any):
        if isinstance(other, self.__class__):
            return self.name == other.name

        return False

    @property
    def url(self) -> str:
        """The URL to the guild's information page on Tibia.com."""
        return tibiapy.urls.get_guild_url(self.name)

    @property
    def url_wars(self) -> str:
        """The URL to the guild's wars page on Tibia.com.

        .. versionadded:: 3.0.0
        """
        return tibiapy.urls.get_guild_wars_url(self.name)


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


class HouseWithId(BaseHouse):
    """Base classes for houses with an ID."""

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
    def url(self) -> str:
        """The URL to the Tibia.com page of the house."""
        return tibiapy.urls.get_house_url(self.world, self.id) if self.id and self.world else None
