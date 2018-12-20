from enum import Enum

__all__ = ('AccountStatus', 'HouseStatus', 'HouseType', 'PvpType', 'Sex', 'TransferType', 'Vocation', 'WorldLocation')


class BaseEnum(Enum):
    def __str__(self):
        return self.value


class AccountStatus(BaseEnum):
    """Possible account statuses."""
    FREE_ACCOUNT = "Free Account"
    PREMIUM_ACCOUNT = "Premium Account"


class HouseStatus(BaseEnum):
    """Renting statuses of a house."""
    RENTED = "rented"
    AUCTIONED = "auctioned"


class HouseType(BaseEnum):
    """
    The types of house available.
    """
    HOUSE = "house"
    GUILDHALL = "guildhall"


class PvpType(BaseEnum):
    """The possible PvP types a World can have."""
    OPEN_PVP = "Open PvP"
    OPTIONAL_PVP = "Optional PvP"
    RETRO_OPEN_PVP = "Retro Open PvP"
    RETRO_HARDCORE_PVP = "Retro Hardcore PvP"
    HARDCORE_PVP = "Hardcore PvP"


class Sex(BaseEnum):
    """Character genders."""
    MALE = "male"
    FEMALE = "female"


class TransferType(BaseEnum):
    """The possible special transfer restrictions a world may have."""
    REGULAR = "regular"  #: No special transfer restrictions.
    BLOCKED = "blocked"  #: Can't transfer to this world, but can transfer out of this world.
    LOCKED = "locked"  #: Can transfer to this world, but can't transfer out of this world.


class Vocation(BaseEnum):
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


class WorldLocation(BaseEnum):
    """The possible physical locations for servers."""
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
