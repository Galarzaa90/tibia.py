from enum import Enum


class AccountStatus(Enum):
    """Possible account statuses."""
    FREE_ACCOUNT = "Free Account"
    PREMIUM_ACCOUNT = "Premium Account"


class HouseStatus(Enum):
    """Renting statuses of a house."""
    RENTED = "rented"
    AUCTIONED = "auctioned"


class HouseType(Enum):
    """
    The types of house available.
    """
    HOUSE = "house"
    GUILDHALL = "guildhall"


class PvpType(Enum):
    """The possible PvP types a World can have."""
    OPEN_PVP = "Open PvP"
    OPTIONAL_PVP = "Optional PvP"
    RETRO_OPEN_PVP = "Retro Open PvP"
    RETRO_HARDCORE_PVP = "Retro Hardcore PvP"


class Sex(Enum):
    """Character genders."""
    MALE = "male"
    FEMALE = "female"


class TransferType(Enum):
    """The possible special transfer restrictions a world may have."""
    REGULAR = "regular" #: No special transfer restrictions.
    BLOCKED = "blocked"  #: Can't transfer to this world, but can transfer out of this world.
    LOCKED = "locked"  #: Can transfer to this world, but can't transfer out of this world.


class Vocation(Enum):
    """
    The possible vocation types.
    """
    NONE = "None"
    DRUID = "Druid"
    KNIGHT = "Knight"
    PALADIN = "Paladin"
    SORCERER = "Sorcerer"
    ELDER_DRUID = "Elder Druid"
    ELITE_KNIGHT = "Elite Knight"
    ROYAL_PALADIN = "Royal Paladin"
    MASTER_SORCERER = "Master Sorcerer"


class WorldLocation(Enum):
    """The possible physical locations for servers."""
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"


def try_enum(cls, val, default=None):
    """Attempts to convert a value into their enum value

    Parameters
    ----------
    cls: :class:`Enum`
        The enum to convert to.
    val:
        The value to try to convert to Enum
    default: optional
        The value to return if no enum value is found.

    Returns
    -------
    The enum value if found, otherwise None
    """
    try:
        return cls(val)
    except ValueError:
        return default
