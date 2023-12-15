"""Models related to characters."""
from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import computed_field

from tibiapy.enums import Sex, Vocation
from tibiapy.models.base import BaseCharacter, BaseGuild, BaseModel, HouseWithId
from tibiapy import urls

__all__ = (
    "AccountBadge",
    "AccountInformation",
    "Achievement",
    "Character",
    "CharacterHouse",
    "Death",
    "DeathParticipant",
    "GuildMembership",
    "OnlineCharacter",
    "OtherCharacter",
)


class AccountBadge(BaseModel):
    """A displayed account badge in the character's information."""

    name: str
    """The name of the badge."""
    icon_url: str
    """The URL to the badge's icon."""
    description: str
    """The description of the badge."""


class AccountInformation(BaseModel):
    """Contains the information of a character's account.

    This is only visible if the character is not marked as hidden.
    """

    created: datetime.datetime
    """The date when the account was created."""
    position: Optional[str] = None
    """The special position of this account, if any."""
    loyalty_title: Optional[str] = None
    """The loyalty title of the account, if any"""


class Achievement(BaseModel):
    """Represents an achievement listed on a character's page."""

    name: str
    """The name of the achievement."""
    grade: int
    """The grade of the achievement, also known as stars."""
    is_secret: bool
    """Whether the achievement is secret or not."""


class CharacterHouse(HouseWithId):
    """A house owned by a character."""

    town: str
    """The town where the city is located in."""
    paid_until: datetime.date
    """The date the last paid rent is due."""


class DeathParticipant(BaseModel):
    """A creature or player that participated in a death, either as a killer o as an assistant.

    A participant can be:

    a) A creature.
    b) A character.
    c) A creature summoned by a character.
    """

    name: str
    """The name of the killer. In the case of summons, the name belongs to the owner."""
    is_player: bool
    """Whether the killer is a player or not."""
    summon: Optional[str] = None
    """The name of the summoned creature, if applicable."""
    is_traded: bool = False
    """If the killer was traded after this death happened."""

    @property
    def url(self) -> Optional[str]:
        """The URL of the character's information page on Tibia.com, if applicable."""
        return urls.get_character_url(self.name) if self.is_player else None


class Death(BaseModel):
    """A character's death."""

    level: int
    """The level at which the death occurred."""
    killers: List[DeathParticipant]
    """A list of all the killers involved."""
    assists: List[DeathParticipant]
    """A list of characters that were involved, without dealing damage."""
    time: datetime.datetime
    """The time at which the death occurred."""

    @property
    def is_by_player(self) -> bool:
        """Whether the kill involves other characters."""
        return any(k.is_player for k in self.killers)

    @property
    def killer(self) -> DeathParticipant:
        """The first killer in the list.

        This is usually the killer that gave the killing blow.
        """
        return self.killers[0] if self.killers else None


class GuildMembership(BaseGuild):
    """The guild information of a character."""

    rank: str
    """The name of the rank the member has."""
    title: Optional[str] = None
    """The title of the member in the guild. This is only available for characters in the forums section."""


class OnlineCharacter(BaseCharacter):
    """An online character in the world's page."""

    vocation: Vocation
    """The vocation of the character."""
    level: int
    """The level of the character."""


class OtherCharacter(BaseCharacter):
    """A character listed in the characters section of a character's page.

    These are only shown if the character is not hidden, and only characters that are not hidden are shown here.
    """

    world: str
    """The name of the world."""
    is_online: bool
    """Whether the character is online or not."""
    is_deleted: bool
    """Whether the character is scheduled for deletion or not."""
    is_traded: bool
    """Whether the character has been traded recently or not."""
    is_main: bool
    """Whether this is the main character or not."""
    position: Optional[str] = None
    """The character's official position, if any."""


class Character(BaseCharacter):
    """A full character from Tibia.com, obtained from its character page."""

    is_traded: bool
    """If the character was traded in the last 6 months."""
    deletion_date: Optional[datetime.datetime] = None
    """The date when the character will be deleted if it is scheduled for deletion. Will be :obj:`None` otherwise."""
    former_names: List[str]
    """Previous names of the character in the last 6 months.."""
    title: Optional[str] = None
    """The character's selected title, if any."""
    unlocked_titles: int = 0
    """The number of titles the character has unlocked."""
    sex: Sex
    """The character's sex."""
    vocation: Vocation
    """The character's vocation."""
    level: int = 2
    """The character's level."""
    achievement_points: int
    """The total of achievement points the character has."""
    world: str
    """The character's current world."""
    former_world: Optional[str] = None
    """The previous world the character was in, in the last 6 months."""
    residence: str
    """The current hometown of the character."""
    married_to: Optional[str] = None
    """The name of the character's spouse. It will be :obj:`None` if not married."""
    houses: List[CharacterHouse]
    """The houses currently owned by the character."""
    guild_membership: Optional[GuildMembership] = None
    """The guild the character is a member of. It will be :obj:`None` if the character is not in a guild."""
    last_login: Optional[datetime.datetime] = None
    """The last time the character logged in. It will be :obj:`None` if the character has never logged in."""
    position: Optional[str] = None
    """The position of the character (e.g. CipSoft Member), if any."""
    comment: Optional[str] = None
    """The displayed comment."""
    is_premium: bool
    """Whether the character's account is Premium or Free."""
    account_badges: List[AccountBadge]
    """The displayed account badges."""
    achievements: List[Achievement]
    """The achievements chosen to be displayed."""
    deaths: List[Death]
    """The character's recent deaths."""
    deaths_truncated: bool
    """Whether the character's deaths are truncated or not.

    In some cases, there are more deaths in the last 30 days than what can be displayed."""
    account_information: Optional[AccountInformation] = None
    """The character's account information. If the character is hidden, this will be :obj:`None`."""
    other_characters: List[OtherCharacter]
    """Other characters in the same account.

    It will be empty if the character is hidden, otherwise, it will contain at least the character itself."""

    # region Properties
    @computed_field
    @property
    def is_scheduled_for_deletion(self) -> bool:
        """Whether the character is scheduled for deletion or not."""
        return self.deletion_date is not None

    @property
    def guild_name(self) -> Optional[str]:
        """The name of the guild the character belongs to, or :obj:`None`."""
        return self.guild_membership.name if self.guild_membership else None

    @property
    def guild_rank(self) -> Optional[str]:
        """The character's rank in the guild they belong to, or :obj:`None`."""
        return self.guild_membership.rank if self.guild_membership else None

    @property
    def guild_url(self) -> Optional[str]:
        """The character's rank in the guild they belong to, or :obj:`None`."""
        return urls.get_guild_url(self.guild_membership.name) if self.guild_membership else None

    @computed_field
    @property
    def is_hidden(self) -> bool:
        """Whether this is a hidden character or not."""
        return len(self.other_characters) == 0

    @property
    def married_to_url(self) -> Optional[str]:
        """The URL to the husband/spouse information page on Tibia.com, if applicable."""
        return urls.get_character_url(self.married_to) if self.married_to else None
    # endregion
