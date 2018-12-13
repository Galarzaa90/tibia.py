from enum import Enum


class Sex(Enum):
    MALE = "male"
    FEMALE = "female"


class HouseStatus(Enum):
    RENTED = "rented"
    AUCTIONED = "auctioned"


class HouseType(Enum):
    HOUSE = "house"
    GUILDHALL = "guildhall"


class AccountStatus(Enum):
    FREE_ACCOUNT = "Free Account"
    PREMIUM_ACCOUNT = "Premium Account"


class Vocation(Enum):
    DRUID = "Druid"
    KNIGHT = "Knight"
    PALADIN = "Paladin"
    SORCERER = "Sorcerer"
    ELDER_DRUID = "Elder Druid"
    ELITE_KNIGHT = "Elite Knight"
    ROYAL_PALADIN = "Royal Paladin"
    MASTER_SORCERER = "Master Sorcerer"


def try_enum(cls, val):
    """Attempts to convert a value into their enum value

    Parameters
    ----------
    cls: :class:`Enum`
        The enum to convert to.
    val:
        The value to try to convert to Enum

    Returns
    -------
    The enum value if found, otherwise None
    """
    try:
        return cls(val)
    except ValueError:
        return None
