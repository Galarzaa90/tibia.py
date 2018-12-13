from enum import Enum


class Sex(Enum):
    FEMALE = "female"
    MALE = "male"


class HouseStatus(Enum):
    AUCTIONED = "auctioned"
    RENTED = "rented"


class HouseType(Enum):
    HOUSE = "house"
    GUILDHALL = "guildhall"


class AccountStatus(Enum):
    FREE_ACCOUNT = "Free Account"
    PREMIUM_ACCOUNT = "Premium Account"


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
