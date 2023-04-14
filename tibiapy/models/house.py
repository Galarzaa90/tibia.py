import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel

from tibiapy import HouseStatus, HouseType, HouseOrder, Sex, abc
from tibiapy.utils import get_tibia_url


__all__ = (
    'BaseHouse',
    'HouseWithId',
    'HouseEntry',
    'House',
    'HousesSection',
)


class BaseHouse(BaseModel):
    name: str
    """The name of the house."""

    @classmethod
    def get_url(cls, house_id, world):
        """Get the Tibia.com URL for a house with the given id and world.

        Parameters
        ----------
        house_id: :class:`int`
            The internal id of the house.
        world: :class:`str`
            The world of the house.

        Returns
        -------
        The URL to the house in Tibia.com
        """
        return get_tibia_url("community", "houses", page="view", houseid=house_id, world=world)


class HouseWithId(BaseHouse):
    id: int
    """The internal ID of the house. This is used on the website to identify houses."""
    world: str
    """The name of the world the house belongs to."""

    def __eq__(self, o: object) -> bool:
        """Two houses are considered equal if their names or ids are equal."""
        if isinstance(o, self.__class__):
            return self.name.lower() == o.name.lower() or self.id == o.id
        return False

    @property
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the house."""
        return self.get_url(self.id, self.world) if self.id and self.world else None


class HouseEntry(HouseWithId):
    """Represents a house from the house list in Tibia.com."""

    """The name of the world the house belongs to."""
    status: HouseStatus
    """The current status of the house."""
    type: HouseType
    """The type of house."""
    town: str
    """The town where the house is located."""
    size: int
    """The size of the house in SQM."""
    rent: int
    """The monthly cost of the house, in gold coins."""
    time_left: Optional[datetime.timedelta]
    """The number of days or hours left until the bid ends, if it has started.
        This is not an exact measure, it is rounded to hours or days."""
    highest_bid: Optional[int]
    """The highest bid so far, if the auction has started."""


class House(HouseWithId):
    """Represents a house in a specific world."""

    status: HouseStatus
    """The current status of the house."""
    type: HouseType
    """The type of the house."""
    image_url: str
    """The URL to the house's minimap image."""
    beds: int
    """The number of beds the house has."""
    size: int
    """The number of SQM the house has."""
    rent: int
    """The monthly cost paid for the house, in gold coins."""
    owner: Optional[str]
    """The current owner of the house, if any."""
    owner_sex: Optional[Sex]
    """The sex of the owner of the house, if applicable."""
    paid_until: Optional[datetime.datetime]
    """The date the last paid rent is due."""
    transfer_date: Optional[datetime.datetime]
    """The date when the owner will move out of the house, if applicable."""
    transferee: Optional[str]
    """The character who will receive the house when the owner moves, if applicable."""
    transfer_price: Optional[int]
    """The price that will be paid from the transferee to the owner for the house transfer."""
    transfer_accepted: Optional[bool]
    """Whether the house transfer has already been accepted or not."""
    highest_bid: Optional[int]
    """The currently highest bid on the house if it is being auctioned."""
    highest_bidder: Optional[str]
    """The character that holds the highest bid."""
    auction_end: Optional[datetime.datetime]
    """The date when the auction will end."""

    @property
    def owner_url(self):
        """:class:`str`: The URL to the Tibia.com page of the house's owner, if applicable."""
        return abc.BaseCharacter.get_url(self.owner) if self.owner is not None else None

    @property
    def transferee_url(self):
        """:class:`str`: The URL to the Tibia.com page of the character receiving the house, if applicable."""
        return abc.BaseCharacter.get_url(self.transferee) if self.transferee is not None else None

    @property
    def highest_bidder_url(self):
        """:class:`str`: The URL to the Tibia.com page of the character with the highest bid, if applicable."""
        return abc.BaseCharacter.get_url(self.highest_bidder) if self.highest_bidder is not None else None


class HousesSection(BaseModel):
    """Represents the house section."""

    world: str
    """The selected world to show houses for."""
    town: str
    """The town to show houses for."""
    status: Optional[HouseStatus] = None
    """The status to show. If :obj:`None`, any status is shown."""
    house_type: HouseType
    """The type of houses to show."""
    order: HouseOrder
    """The ordering to use for the results."""
    entries: List[HouseEntry]
    """The houses matching the filters."""
    available_worlds: List[str]
    """The list of available worlds to choose from."""
    available_towns: List[str]
    """The list of available towns to choose from."""

    @property
    def url(self):
        """:class:`str`: Get the URL to the houses section with the current parameters."""
        return self.get_url(self.world, self.town, self.house_type, self.status, self.order)

    @classmethod
    def _get_query_params(cls, world, town, house_type, status=None, order=None) -> Dict[str, str]:
        """Build the query parameters for a house search.

        Parameters
        ----------
        world: :class:`str`
            The world to search for houses in.
        town: :class:`str`
            The town to search houses in.
        house_type: :class:`HouseType`
            The type of houses to filter.
        status: :class:`HouseStatus`, optional
            The status of the house to filter. If undefined, all status will be included.
        order: :class:`HouseOrder`
            The field to order houses by.

        Returns
        -------
        :class:`dict`
            The query parameters representing for a house search.
        """
        params = {
            "world": world,
            "town": town,
            "type": house_type.plural if house_type else None,
            "state": status.value if status else None,
            "order": order.value if order else None,
        }
        return {k: v for k, v in params.items() if v is not None}

    @classmethod
    def get_url(cls, world, town, house_type, status=None, order=None):
        """Get the URL to the house list on Tibia.com with the specified filters.

        Parameters
        ----------
        world: :class:`str`
            The world to search in.
        town: :class:`str`
            The town to show results for.
        house_type: :class:`HouseType`
            The type of houses to show.
        status: :class:`HouseStatus`
            The status of the houses to show.
        order: :class:`HouseOrder`
            The sorting parameter to use for the results.

        Returns
        -------
        :class:`str`
            The URL to the list matching the parameters.
        """
        query = cls._get_query_params(world, town, house_type, status, order)
        return get_tibia_url("community", "houses", **query)




