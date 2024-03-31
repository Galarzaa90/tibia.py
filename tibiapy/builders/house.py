from __future__ import annotations


from typing import List, TYPE_CHECKING, Optional

from typing_extensions import Self

from tibiapy.models.house import HouseEntry, HousesSection, House

if TYPE_CHECKING:
    import datetime
    from tibiapy.enums import HouseStatus, HouseType, HouseOrder, Sex


class HousesSectionBuilder:
    def __init__(self):
        self._world = None
        self._town = None
        self._status = None
        self._house_type = None
        self._order = None
        self._entries = []
        self._available_worlds = []
        self._available_towns = []

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def town(self, town: str) -> Self:
        self._town = town
        return self

    def status(self, status: HouseStatus) -> Self:
        self._status = status
        return self

    def house_type(self, house_type: HouseType) -> Self:
        self._house_type = house_type
        return self

    def order(self, order: HouseOrder) -> Self:
        self._order = order
        return self

    def entries(self, entries: List[HouseEntry]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry: HouseEntry) -> Self:
        self._entries.append(entry)
        return self

    def available_worlds(self, available_worlds: List[str]) -> Self:
        self._available_worlds = available_worlds
        return self

    def available_towns(self, available_towns: List[str]) -> Self:
        self._available_towns = available_towns
        return self

    def build(self) -> HousesSection:
        return HousesSection(
            world=self._world,
            town=self._town,
            status=self._status,
            house_type=self._house_type,
            order=self._order,
            entries=self._entries,
            available_worlds=self._available_worlds,
            available_towns=self._available_towns,
        )


class _HouseWithIdBuilder:
    def __init__(self):
        self._id = None
        self._name = None
        self._world = None

    def id(self, id: int):
        self._id = id
        return self

    def world(self, world: str):
        self._world = world
        return self

    def name(self, name: str):
        self._name = name
        return self


class HouseEntryBuilder(_HouseWithIdBuilder):
    def __init__(self):
        super().__init__()
        self._town = None
        self._size = None
        self._status = None
        self._type = None
        self._rent = None
        self._time_left = None
        self._highest_bid = None

    def status(self, status: HouseStatus) -> Self:
        self._status = status
        return self

    def type(self, type: HouseType) -> Self:
        self._type = type
        return self

    def town(self, town: str) -> Self:
        self._town = town
        return self

    def size(self, size: int) -> Self:
        self._size = size
        return self

    def rent(self, rent: int) -> Self:
        self._rent = rent
        return self

    def time_left(self, time_left: Optional[datetime.timedelta]) -> Self:
        self._time_left = time_left
        return self

    def highest_bid(self, highest_bid: Optional[int]) -> Self:
        self._highest_bid = highest_bid
        return self

    def build(self) -> HouseEntry:
        return HouseEntry(
            name=self._name,
            id=self._id,
            world=self._world,
            status=self._status,
            type=self._type,
            town=self._town,
            size=self._size,
            rent=self._rent,
            time_left=self._time_left,
            highest_bid=self._highest_bid,
        )


class HouseBuilder(_HouseWithIdBuilder):
    def __init__(self):
        super().__init__()
        self._status = None
        self._type = None
        self._rent = None
        self._beds = None
        self._size = None
        self._image_url = None
        self._owner = None
        self._owner_sex = None
        self._paid_until = None
        self._transfer_date = None
        self._transfer_recipient = None
        self._transfer_price = None
        self._transfer_accepted = None
        self._highest_bid = None
        self._highest_bidder = None
        self._auction_end = None

    def status(self, status: HouseStatus) -> Self:
        self._status = status
        return self

    def rent(self, rent: int) -> Self:
        self._rent = rent
        return self

    def type(self, type: HouseType) -> Self:
        self._type = type
        return self

    def image_url(self, image_url: str) -> Self:
        self._image_url = image_url
        return self

    def beds(self, beds: int) -> Self:
        self._beds = beds
        return self

    def size(self, size: int) -> Self:
        self._size = size
        return self

    def owner(self, owner: Optional[str]) -> Self:
        self._owner = owner
        return self

    def owner_sex(self, owner_sex: Sex) -> Self:
        self._owner_sex = owner_sex
        return self

    def paid_until(self, paid_until: Optional[datetime.datetime]) -> Self:
        self._paid_until = paid_until
        return self

    def transfer_date(self, transfer_date: Optional[datetime.datetime]) -> Self:
        self._transfer_date = transfer_date
        return self

    def transfer_recipient(self, transfer_recipient: Optional[str]) -> Self:
        self._transfer_recipient = transfer_recipient
        return self

    def transfer_price(self, transfer_price: Optional[int]) -> Self:
        self._transfer_price = transfer_price
        return self

    def transfer_accepted(self, transfer_accepted: Optional[bool]) -> Self:
        self._transfer_accepted = transfer_accepted
        return self

    def highest_bid(self, highest_bid: Optional[int]) -> Self:
        self._highest_bid = highest_bid
        return self

    def highest_bidder(self, highest_bidder: Optional[str]) -> Self:
        self._highest_bidder = highest_bidder
        return self

    def auction_end(self, auction_end: Optional[datetime.datetime]) -> Self:
        self._auction_end = auction_end
        return self

    def build(self) -> House:
        return House(
            name=self._name,
            id=self._id,
            world=self._world,
            status=self._status,
            type=self._type,
            size=self._size,
            rent=self._rent,
            image_url=self._image_url,
            beds=self._beds,
            owner=self._owner,
            owner_sex=self._owner_sex,
            paid_until=self._paid_until,
            transfer_recipient=self._transfer_recipient,
            transfer_price=self._transfer_price,
            transfer_date=self._transfer_date,
            transfer_accepted=self._transfer_accepted,
            highest_bid=self._highest_bid,
            highest_bidder=self._highest_bidder,
            auction_end=self._auction_end,
        )
