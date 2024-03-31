"""Enumerations used by models throughout the library."""
from __future__ import annotations

from enum import Enum, Flag, IntEnum
from typing import Any, Optional, TYPE_CHECKING

from pydantic_core import core_schema
from typing_extensions import Self

from tibiapy.errors import EnumValueError
from tibiapy.utils import try_enum

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import CoreSchema

__all__ = (
    "AuctionBattlEyeFilter",
    "AuctionOrderBy",
    "AuctionOrderDirection",
    "PvpTypeFilter",
    "AuctionSearchType",
    "AuctionSkillFilter",
    "AuctionStatus",
    "AuctionVocationFilter",
    "AvailableForumSection",
    "BattlEyeType",
    "BazaarType",
    "BidType",
    "HighscoresBattlEyeType",
    "HighscoresCategory",
    "HighscoresProfession",
    "HouseOrder",
    "HouseStatus",
    "HouseType",
    "NewsCategory",
    "NewsType",
    "PvpType",
    "Sex",
    "SpellGroup",
    "SpellSorting",
    "SpellType",
    "SpellVocationFilter",
    "ThreadStatus",
    "TransferType",
    "Vocation",
    "WorldLocation",
)


class StringEnum(str, Enum):

    @classmethod
    def validate(cls, v: Any) -> Self:
        e = try_enum(cls, v)
        if e is None:
            raise EnumValueError(cls, v)

        return e

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            lambda x: cls.validate(x),
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.value),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: CoreSchema, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"enum": [m.value for m in cls], "type": "string"}


class NumericEnum(IntEnum):
    def __str__(self):
        return self.name.lower()

    @classmethod
    def validate(cls, v: Any):
        e = try_enum(cls, v)
        if e is None:
            raise EnumValueError(cls, v)

        return e

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            lambda x: cls.validate(x),
            core_schema.any_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: x.name),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: CoreSchema, _handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"enum": [m.name for m in cls], "type": "string"}


class AuctionBattlEyeFilter(NumericEnum):
    """The possible BattlEye filters that can be used for auctions."""

    INITIALLY_PROTECTED = 1
    """Worlds protected from the beginning, represented by a green symbol."""
    PROTECTED = 2
    """Worlds protected after the world was created, represented by a yellow symbol."""
    NOT_PROTECTED = 3
    """Worlds without any BattlEye protection."""
    YELLOW = PROTECTED
    """Alias for protected worlds.

    .. versionadded:: 4.0.0
    """
    GREEN = INITIALLY_PROTECTED
    """Alias for initially protected worlds.

    .. versionadded:: 4.0.0
    """


class AuctionOrderDirection(NumericEnum):
    """The possible ordering directions for auctions.

    The field or value used for the ordering is defined by :class:`AuctionOrderBy`.
    """

    HIGHEST_LATEST = 0
    """Order by the highest or latest value."""
    LOWEST_EARLIEST = 1
    """Order by the lowest or earliest value."""


class AuctionOrderBy(NumericEnum):
    """The possible values to order the auctions by."""

    BID = 100
    """The currently displayed bid for the auction."""
    END_DATE = 101
    """The end date of the auction."""
    LEVEL = 102
    """The experience level of the auctioned character."""
    START_DATE = 103
    """The start date of the auction."""
    AXE_FIGHTING = 10
    CLUB_FIGHTING = 9
    DISTANCE_FIGHTING = 7
    FISHING = 13
    FIST_FIGHTING = 11
    MAGIC_LEVEL = 1
    SHIELDING = 6
    SWORD_FIGHTING = 8


class PvpTypeFilter(NumericEnum):
    """The possible PVP filters that can be used for auctions."""

    OPEN_PVP = 0
    OPTIONAL_PVP = 1
    HARDCORE_PVP = 2
    RETRO_OPEN_PVP = 3
    RETRO_HARDCORE_PVP = 4


class AuctionSearchType(NumericEnum):
    """The possible search types."""

    ITEM_DEFAULT = 0
    """Searches everything that includes the words on the search string."""
    ITEM_WILDCARD = 1
    """Searches everything that includes the search string"""
    CHARACTER_NAME = 2
    """Searches a character's name."""


class AuctionStatus(StringEnum):
    """The possible values an auction might have."""

    IN_PROGRESS = "in progress"
    """The auction is currently active.

    Notes
    -----
    This status doesn't exist in Tibia.com explicitly. It is given to all ongoing auctions."""
    CURRENTLY_PROCESSED = "currently processed"
    """The auction ended with a winner, but payment hasn't been received yet."""
    PENDING_TRANSFER = "will be transferred at the next server save"
    """The auction was finished and was paid, but the character hasn't been transferred to the new owner yet."""
    CANCELLED = "cancelled"
    """The auction was cancelled as no payment was received in time."""
    FINISHED = "finished"
    """The auction either finished with no bids or the character was transferred to the new owner already."""


class AuctionSkillFilter(NumericEnum):
    """The different skill filters for auctions."""

    AXE_FIGHTING = 10
    CLUB_FIGHTING = 9
    DISTANCE_FIGHTING = 7
    FISHING = 13
    FIST_FIGHTING = 11
    MAGIC_LEVEL = 1
    SHIELDING = 6
    SWORD_FIGHTING = 8


class AuctionVocationFilter(NumericEnum):
    """The possible vocation filters for auctions."""

    NONE = 1
    DRUID = 2
    KNIGHT = 3
    PALADIN = 4
    SORCERER = 5


class AvailableForumSection(StringEnum):
    """The available forum sections and their URL query parameter values."""

    WORLD_BOARDS = "worldboards"
    TRADE_BOARDS = "tradeboards"
    COMMUNITY_BOARDS = "communityboards"
    SUPPORT_BOARDS = "supportboards"
    GUILD_BOARDS = "guildboards"


class BattlEyeType(NumericEnum):
    """The possible BattlEye statuses a world can have.

    .. versionadded:: 4.0.0
    """

    UNPROTECTED = 0
    """Worlds without any BattlEye protection."""
    PROTECTED = 1
    """Worlds protected after the world was created, represented by a yellow symbol."""
    INITIALLY_PROTECTED = 2
    """Worlds protected from the beginning, represented by a green symbol."""
    YELLOW = PROTECTED
    """Alias for protected worlds."""
    GREEN = INITIALLY_PROTECTED
    """Alias for initially protected worlds."""


class BazaarType(StringEnum):
    """The possible bazaar types."""

    CURRENT = "Current Auctions"
    HISTORY = "Auction History"

    @property
    def subtopic(self) -> str:
        """The subtopic argument for this Bazaar type."""
        return "currentcharactertrades" if self == self.CURRENT else "pastcharactertrades"


class BidType(StringEnum):
    """The possible bid types for an auction."""

    MINIMUM = "Minimum Bid"
    """The minimum bid set by the auction author, meaning the auction hasn't received any bids or it finished
     without bids."""
    CURRENT = "Current Bid"
    """The current maximum bid, meaning the auction has received at least one bid."""
    WINNING = "Winning Bid"
    """The bid that won the auction."""


class HighscoresBattlEyeType(NumericEnum):
    """The possible BattlEye filters that can be used for highscores."""

    ANY_WORLD = -1
    """Show all worlds."""

    INITIALLY_PROTECTED = 2
    """Worlds protected from the beginning, represented by a green symbol."""
    PROTECTED = 1
    """Worlds protected after the world was created, represented by a yellow symbol."""
    UNPROTECTED = 0
    """Worlds without any BattlEye protection."""
    YELLOW = PROTECTED
    """Alias for protected worlds.

    .. versionadded:: 4.0.0
    """
    GREEN = INITIALLY_PROTECTED
    """Alias for initially protected worlds.

    .. versionadded:: 4.0.0
    """


class HighscoresCategory(NumericEnum):
    """The different highscores categories."""

    ACHIEVEMENTS = 1
    AXE_FIGHTING = 2
    BOSS_POINTS = 15
    CHARM_POINTS = 3
    CLUB_FIGHTING = 4
    DISTANCE_FIGHTING = 5
    DROME_SCORE = 14
    EXPERIENCE = 6
    FISHING = 7
    FIST_FIGHTING = 8
    GOSHNARS_TAINT = 9
    LOYALTY_POINTS = 10
    MAGIC_LEVEL = 11
    SHIELDING = 12
    SWORD_FIGHTING = 13


class HighscoresProfession(NumericEnum):
    """The vocation filters available for Highscores.

    The numeric values are what the highscores form accepts.
    """

    ALL = 0
    NONE = 1
    KNIGHTS = 2
    PALADINS = 3
    SORCERERS = 4
    DRUIDS = 5

    @classmethod
    def from_name(cls, name: str, all_fallback: bool = True) -> Optional[Self]:
        """Get a vocation filter from a vocation's name.

        Parameters
        ----------
        name: :class:`str`
            The name of the vocation.
        all_fallback: :class:`bool`
            Whether to return :py:attr:`ALL` if no match is found. Otherwise, :obj:`None` will be returned.

        Returns
        -------
        HighscoresProfession, optional:
            The matching vocation filter.
        """
        name = name.upper()
        for vocation in cls:  # type: HighscoresProfession
            if vocation.name in name or vocation.name[:-1] in name and vocation != cls.ALL:
                return vocation

        if all_fallback or name.upper() == "ALL":
            return cls.ALL

        return None


class HouseOrder(StringEnum):
    """The possible ordering methods for house lists in Tibia.com."""

    NAME = "name"
    SIZE = "size"
    RENT = "rent"
    BID = "bid"
    AUCTION_END = "end"


class HouseStatus(StringEnum):
    """Renting statuses of a house."""

    RENTED = "rented"
    AUCTIONED = "auctioned"


class HouseType(StringEnum):
    """The types of house available."""

    HOUSE = "house"
    GUILDHALL = "guildhall"

    @property
    def plural(self) -> str:
        """:class:`str`: The plural for the house type."""
        return f"{self.value}s"


class NewsCategory(StringEnum):
    """The different news categories."""

    CIPSOFT = "cipsoft"
    COMMUNITY = "community"
    DEVELOPMENT = "development"
    SUPPORT = "support"
    TECHNICAL_ISSUES = "technical"

    @property
    def filter_name(self) -> str:
        """The name of the filter parameter for this value."""
        return f"filter_{self.value}"

    @property
    def big_icon_url(self) -> str:
        """The URL to the big icon representing this category."""
        from tibiapy.urls import get_static_file_url
        return get_static_file_url("images", "global", "content", f"newsicon_{self.value}_big.gif")

    @property
    def small_icon_url(self) -> str:
        """The URL to the small icon representing this category."""
        from tibiapy.urls import get_static_file_url
        return get_static_file_url("images", "global", "content", f"newsicon_{self.value}_small.gif")


class NewsType(StringEnum):
    """The different types of new entries."""

    NEWS_TICKER = "News Ticker"
    FEATURED_ARTICLE = "Featured Article"
    NEWS = "News"

    @property
    def filter_name(self) -> str:
        """The filter parameter name for this value."""
        return f"filter_{self.value.split(' ')[-1].lower()}"

    @property
    def filter_value(self) -> str:
        """The filter parameter value for this value."""
        return self.value.split(" ")[-1].lower()


class PvpType(StringEnum):
    """The possible PvP types a World can have."""

    OPEN_PVP = "Open PvP"
    OPTIONAL_PVP = "Optional PvP"
    RETRO_OPEN_PVP = "Retro Open PvP"
    RETRO_HARDCORE_PVP = "Retro Hardcore PvP"
    HARDCORE_PVP = "Hardcore PvP"


class Sex(StringEnum):
    """Possible character sexes."""

    MALE = "male"
    FEMALE = "female"


class SpellGroup(StringEnum):
    """The possible cooldown groups.

    Note that secondary groups are not enumerated.
    """

    ATTACK = "Attack"
    HEALING = "Healing"
    SUPPORT = "Support"


class SpellSorting(StringEnum):
    """The different sorting options for the spells section."""

    NAME = "name"
    GROUP = "group"
    TYPE = "type"
    EXP_LEVEL = "level"
    MANA = "mana"
    PRICE = "price"
    PREMIUM = "premium"


class SpellType(StringEnum):
    """The possible spell types."""

    INSTANT = "Instant"
    RUNE = "Rune"


class SpellVocationFilter(StringEnum):
    """The possible vocation types to filter out spells."""

    DRUID = "Druid"
    KNIGHT = "Knight"
    PALADIN = "Paladin"
    SORCERER = "Sorcerer"


class ThreadStatus(Flag):
    """The possible status a thread can have.

    Threads can have a combination of multiple status. The numeric values are arbitrary.
    """

    NONE = 0
    HOT = 1  #: Thread has more than 16 replies.
    NEW = 2  #: Thread has new posts since last visit.
    CLOSED = 4  #: Thread is closed.
    STICKY = 8  #: Thread is stickied.

    def __str__(self):
        return ", ".join(v.name.title() for v in list(self))

    def __iter__(self):
        for entry in list(self.__class__):
            if entry in self and entry is not self.NONE:
                yield entry

    def get_icon_name(self) -> Optional[str]:
        """Generate an icon name, following the same ordering used in Tibia.com.

        Returns
        -------
        :class:`str`
            The name of the icon used in Tibia.com
        """
        if self.value == 0:
            return None

        joined_str = "".join(v.name.lower() for v in list(self))
        return f"logo_{joined_str}.gif"

    @classmethod
    def from_icon(cls, icon: str) -> Self:
        """Get the flag combination, based from the icon's name present in the thread status.

        Parameters
        ----------
        icon: :class:`str`
            The icon's filename.

        Returns
        -------
        :class:`ThreadStatus`
            The combination of thread status founds.
        """
        flags = 0
        for entry in list(cls):
            if entry.name.lower() in icon:
                flags += entry.value
        # noinspection PyArgumentList
        return cls(flags)


class TransferType(StringEnum):
    """The possible special transfer restrictions a world may have."""

    REGULAR = "regular"  #: No special transfer restrictions
    BLOCKED = "blocked"  #: Can't transfer to this world, but can transfer out of this world.
    LOCKED = "locked"  #: Can transfer to this world, but can't transfer out of this world.


class Vocation(StringEnum):
    """The possible vocation types."""

    NONE = "None"
    DRUID = "Druid"
    KNIGHT = "Knight"
    PALADIN = "Paladin"
    SORCERER = "Sorcerer"
    ELDER_DRUID = "Elder Druid"
    ELITE_KNIGHT = "Elite Knight"
    ROYAL_PALADIN = "Royal Paladin"
    MASTER_SORCERER = "Master Sorcerer"

    @property
    def base(self) -> Self:
        """The base vocation of this vocation if promoted. If not promoted, the same value is returned."""
        if self == self.ELDER_DRUID:
            return self.DRUID
        if self == self.MASTER_SORCERER:
            return self.SORCERER
        if self == self.ROYAL_PALADIN:
            return self.PALADIN
        if self == self.ELITE_KNIGHT:
            return self.KNIGHT
        return self


class WorldLocation(StringEnum):
    """The possible physical locations for servers."""

    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
