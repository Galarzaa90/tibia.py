from __future__ import annotations

import datetime
from typing import Optional, List

from pydantic import BaseModel

from tibiapy import Sex, Vocation, AccountStatus, abc
from tibiapy.utils import get_tibia_url


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

    This is only visible if the character is not marked as hidden.Attributes
    ----------
    created: :class:`datetime.datetime`
        The date when the account was created.
    position: :class:`str`, optional
        The special position of this account, if any.
    loyalty_title: :class:`str`, optional
        The loyalty title of the account, if any.
    """

    created: datetime.datetime
    """The date when the account was created."""
    position: Optional[str] = None
    """The special position of this account, if any."""
    loyalty_title: Optional[str] = None
    """The loyalty title of the account, if any"""


class Achievement(BaseModel):
    name: str
    """The name of the achievement."""
    grade: int
    """The grade of the achievement, also known as stars."""
    secret: bool = False
    """Whether the achievement is secret or not."""


class BaseCharacter(BaseModel):
    name: str

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


class Character(BaseCharacter):
    """A full character from Tibia.com, obtained from its character page."""

    traded: bool = False
    """If the character was traded in the last 6 months."""
    deletion_date: Optional[datetime.datetime] = None
    """The date when the character will be deleted if it is scheduled for deletion. Will be :obj:`None` otherwise."""
    former_names: List[str] = []
    """Previous names of the character."""
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
    houses: List['CharacterHouse'] = []
    """The houses currently owned by the character."""
    guild_membership: Optional['GuildMembership'] = None
    """The guild the character is a member of. It will be :obj:`None` if the character is not in a guild."""
    last_login: Optional[datetime.datetime] = None
    """The last time the character logged in. It will be :obj:`None` if the character has never logged in."""
    position: Optional[str] = None
    """The position of the character (e.g. CipSoft Member), if any."""
    comment: Optional[str] = None
    """The displayed comment."""
    account_status: AccountStatus
    """Whether the character's account is Premium or Free."""
    account_badges: List[AccountBadge] = []
    """The displayed account badges."""
    achievements: List[Achievement] = []
    """The achievements chosen to be displayed."""
    deaths: List['Death'] = []
    """The character's recent deaths."""
    deaths_truncated: bool = False
    """Whether the character's deaths are truncated or not.

    In some cases, there are more deaths in the last 30 days than what can be displayed."""
    account_information: Optional[AccountInformation] = None
    """The character's account information. If the character is hidden, this will be :obj:`None`."""
    other_characters: List['OtherCharacter'] = []
    """Other characters in the same account.

    It will be empty if the character is hidden, otherwise, it will contain at least the character itself."""

    # region Properties
    @property
    def deleted(self) -> bool:
        """:class:`bool`: Whether the character is scheduled for deletion or not."""
        return self.deletion_date is not None

    @property
    def guild_name(self) -> Optional[str]:
        """:class:`str`, optional: The name of the guild the character belongs to, or :obj:`None`."""
        return self.guild_membership.name if self.guild_membership else None

    @property
    def guild_rank(self) -> Optional[str]:
        """:class:`str`, optional: The character's rank in the guild they belong to, or :obj:`None`."""
        return self.guild_membership.rank if self.guild_membership else None

    @property
    def guild_url(self) -> Optional[str]:
        """:class:`str`, optional: The character's rank in the guild they belong to, or :obj:`None`."""
        return abc.BaseGuild.get_url(self.guild_membership.name) if self.guild_membership else None

    @property
    def hidden(self) -> bool:
        """:class:`bool`: Whether this is a hidden character or not."""
        return len(self.other_characters) == 0

    @property
    def married_to_url(self) -> Optional[str]:
        """:class:`str`, optional: The URL to the husband/spouse information page on Tibia.com, if applicable."""
        return self.get_url(self.married_to) if self.married_to else None
    # endregion


class Death(BaseModel):
    """A character's death."""

    name: str
    """The name of the character this death belongs to."""
    level: int
    """The level at which the death occurred."""
    killers: List['Killer']
    """A list of all the killers involved."""
    assists: List['Killer']
    """A list of characters that were involved, without dealing damage."""
    time: datetime.datetime
    """The time at which the death occurred."""

    @property
    def by_player(self):
        """:class:`bool`: Whether the kill involves other characters."""
        return any(k.player and self.name != k.name for k in self.killers)

    @property
    def killer(self):
        """:class:`Killer`: The first killer in the list.

        This is usually the killer that gave the killing blow.
        """
        return self.killers[0] if self.killers else None


class GuildMembership(BaseModel):
    name: str
    """The name of the guild."""
    rank: str
    """The name of the rank the member has."""
    title: Optional[str] = None
    """The title of the member in the guild. This is only available for characters in the forums section."""


class Killer(BaseModel):
    """Represents a killer.

    A killer can be:

    a) A creature.
    b) A character.
    c) A creature summoned by a character."""
    name: str
    """The name of the killer. In the case of summons, the name belongs to the owner."""
    player: bool
    """Whether the killer is a player or not."""
    summon: Optional[str] = None
    """The name of the summoned creature, if applicable."""
    traded: bool = False
    """If the killer was traded after this death happened."""

    @property
    def url(self):
        """:class:`str`, optional: The URL of the character’s information page on Tibia.com, if applicable."""
        return Character.get_url(self.name) if self.player else None


class OnlineCharacter(BaseCharacter):
    """An online character in the world's page."""
    vocation: Vocation
    """The vocation of the character."""
    level: int
    """The level of the character."""


class OtherCharacter(BaseCharacter):
    """A character listed in the characters section of a character's page.

    These are only shown if the character is not hidden, and only characters that are not hidden are shown here."""

    world: str
    """The name of the world."""
    online: bool
    """Whether the character is online or not."""
    deleted: bool
    """Whether the character is scheduled for deletion or not."""
    traded: bool
    """Whether the character has been traded recently or not."""
    main: bool
    """Whether this is the main character or not."""
    position: Optional[str]
    """The character's official position, if any."""
