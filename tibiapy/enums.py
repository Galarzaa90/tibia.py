from enum import Enum


class Sex(Enum):
    FEMALE = "female"
    MALE = "male"


class HouseStatus(Enum):
    AUCTIONED = "auctioned"
    RENTED = "rented"
