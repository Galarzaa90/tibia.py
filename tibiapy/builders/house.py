from __future__ import annotations

import datetime
from typing import List, TYPE_CHECKING, Optional

from tibiapy.models.house import HouseEntry, HousesSection, House

if TYPE_CHECKING:
    from tibiapy import HouseStatus, HouseType, HouseOrder



class HousesSectionBuilder:
    def __init__(self, **kwargs):
        self._world = kwargs.get("world")
        self._town = kwargs.get("town")
        self._status = kwargs.get("status")
        self._house_type = kwargs.get("house_type")
        self._order = kwargs.get("order")
        self._entries = kwargs.get("entries") or []
        self._available_worlds = kwargs.get("available_worlds")
        self._available_towns = kwargs.get("available_towns")

    def world(self, world: str) -> 'HousesSectionBuilder':
        self._world = world
        return self

    def town(self, town:  str) -> 'HousesSectionBuilder':
        self._town = town
        return self

    def status(self, status: HouseStatus) -> 'HousesSectionBuilder':
        self._status = status
        return self

    def house_type(self, house_type: HouseType) -> 'HousesSectionBuilder':
        self._house_type = house_type
        return self

    def order(self, order: HouseOrder) -> 'HousesSectionBuilder':
        self._order = order
        return self

    def entries(self, entries: List[HouseEntry]) -> 'HousesSectionBuilder':
        self._entries = entries
        return self

    def add_entry(self, entry: HouseEntry) -> 'HousesSectionBuilder':
        self._entries.append(entry)
        return self

    def available_worlds(self, available_worlds: List[str]) -> 'HousesSectionBuilder':
        self._available_worlds = available_worlds
        return self

    def available_towns(self, available_towns: List[str]) -> 'HousesSectionBuilder':
        self._available_towns = available_towns
        return self

    def build(self):
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
    def __init__(self, **kwargs):
        self._id = kwargs.get("id")
        self._name = kwargs.get("name")
        self._world = kwargs.get("world")

    def id(self, id: int) -> '_HouseWithIdBuilder':
        self._id = id
        return self

    def world(self, world: int) -> '_HouseWithIdBuilder':
        self._world = world
        return self

    def name(self, name: int) -> '_HouseWithIdBuilder':
        self._name = name
        return self


class HouseEntryBuilder(_HouseWithIdBuilder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._town = kwargs.get("town")
        self._size = kwargs.get("size")
        self._status = kwargs.get("status")
        self._type = kwargs.get("type")
        self._rent = kwargs.get("rent")
        self._time_left = kwargs.get("time_left")
        self._highest_bid = kwargs.get("highest_bid")

    def status(self, status: HouseStatus) -> 'HouseBuilder':
        self._status = status
        return self

    def type(self, type: HouseType) -> 'HouseEntryBuilder':
        self._type = type
        return self

    def town(self, town: int) -> 'HouseEntryBuilder':
        self._town = town
        return self

    def size(self, size: int) -> 'HouseEntryBuilder':
        self._size = size
        return self

    def rent(self, rent: int) -> 'HouseEntryBuilder':
        self._rent = rent
        return self

    def time_left(self, time_left: Optional[datetime.timedelta]) -> 'HouseEntryBuilder':
        self._time_left = time_left
        return self

    def highest_bid(self, highest_bid: Optional[int]) -> 'HouseEntryBuilder':
        self._highest_bid = highest_bid
        return self

    def build(self):
        return HouseEntry(
            name=self._name,
            id=self._id,
            world=self._world,
            status=self._status,
            type=self._type,
            town=self._town,
            size=self._size,
            rent=self._rent,
        )


class HouseBuilder(_HouseWithIdBuilder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = kwargs.get("status")
        self._type = kwargs.get("type")
        self._rent = kwargs.get("rent")
        self._beds = kwargs.get("beds")
        self._size = kwargs.get("size")
        self._image_url = kwargs.get("image_url")
        self._owner = kwargs.get("owner")
        self._owner_sex = kwargs.get("owner_sex")
        self._paid_until = kwargs.get("paid_until")
        self._transfer_date = kwargs.get("transfer_date")
        self._transferee = kwargs.get("transferee")
        self._transfer_price = kwargs.get("transfer_price")
        self._transfer_accepted = kwargs.get("transfer_accepted")
        self._highest_bid = kwargs.get("highest_bid")
        self._highest_bidder = kwargs.get("highest_bidder")
        self._auction_end = kwargs.get("auction_end")

    def status(self, status: HouseStatus) -> 'HouseBuilder':
        self._status = status
        return self

    def rent(self, rent: int) -> 'HouseBuilder':
        self._rent = rent
        return self

    def type(self, type: HouseType) -> 'HouseBuilder':
        self._type = type
        return self

    def image_url(self, image_url: str) -> 'HouseBuilder':
        self._image_url = image_url
        return self

    def beds(self, beds: int) -> 'HouseBuilder':
        self._beds = beds
        return self

    def size(self, size: int) -> 'HouseBuilder':
        self._size = size
        return self

    def owner(self, owner: int) -> 'HouseBuilder':
        self._owner = owner
        return self

    def owner_sex(self, owner_sex: int) -> 'HouseBuilder':
        self._owner_sex = owner_sex
        return self

    def paid_until(self, paid_until: int) -> 'HouseBuilder':
        self._paid_until = paid_until
        return self

    def transfer_date(self, transfer_date: int) -> 'HouseBuilder':
        self._transfer_date = transfer_date
        return self

    def transferee(self, transferee: int) -> 'HouseBuilder':
        self._transferee = transferee
        return self

    def transfer_price(self, transfer_price: int) -> 'HouseBuilder':
        self._transfer_price = transfer_price
        return self

    def transfer_accepted(self, transfer_accepted: int) -> 'HouseBuilder':
        self._transfer_accepted = transfer_accepted
        return self

    def highest_bid(self, highest_bid: int) -> 'HouseBuilder':
        self._highest_bid = highest_bid
        return self

    def highest_bidder(self, highest_bidder: str) -> 'HouseBuilder':
        self._highest_bidder = highest_bidder
        return self

    def auction_end(self, auction_end: int) -> 'HouseBuilder':
        self._auction_end = auction_end
        return self

    def build(self):
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
            transfer_price=self._transfer_price,
            transfer_accepted=self._transfer_accepted,
            highest_bid=self._highest_bid,
            highest_bidder=self._highest_bidder,
        )
