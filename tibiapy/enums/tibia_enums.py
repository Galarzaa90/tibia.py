from enum import Enum


class Gender(Enum):
    FEMALE = "female"
    MALE = "male"


class HouseStatus(Enum):
    AUCTIONED = "auctioned"
    RENTED = "rented"
