"""Models for the houses section."""
import datetime
from typing import List, Optional

from tibiapy.enums import HouseStatus, HouseType, HouseOrder, Sex
from tibiapy.models import HouseWithId, BaseModel
from tibiapy.urls import get_character_url, get_houses_section_url

__all__ = (
    "HouseEntry",
    "House",
    "HousesSection",
)


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
    time_left: Optional[datetime.timedelta] = None
    """The number of days or hours left until the bid ends, if it has started.
        This is not an exact measure, it is rounded to hours or days."""
    highest_bid: Optional[int] = None
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
    owner: Optional[str] = None
    """The current owner of the house, if any."""
    owner_sex: Optional[Sex] = None
    """The sex of the owner of the house, if applicable."""
    paid_until: Optional[datetime.datetime] = None
    """The date the last paid rent is due."""
    transfer_date: Optional[datetime.datetime] = None
    """The date when the owner will move out of the house, if applicable."""
    transfer_recipient: Optional[str] = None
    """The character who will receive the house when the owner moves, if applicable."""
    transfer_price: Optional[int] = None
    """The price that will be paid from the transferee to the owner for the house transfer."""
    transfer_accepted: Optional[bool] = None
    """Whether the house transfer has already been accepted or not."""
    highest_bid: Optional[int] = None
    """The currently highest bid on the house if it is being auctioned."""
    highest_bidder: Optional[str] = None
    """The character that holds the highest bid."""
    auction_end: Optional[datetime.datetime] = None
    """The date when the auction will end."""

    @property
    def owner_url(self) -> Optional[str]:
        """The URL to the Tibia.com page of the house's owner, if applicable."""
        return get_character_url(self.owner) if self.owner is not None else None

    @property
    def transferee_url(self) -> Optional[str]:
        """The URL to the Tibia.com page of the character receiving the house, if applicable."""
        return get_character_url(self.transfer_recipient) if self.transfer_recipient is not None else None

    @property
    def highest_bidder_url(self) -> Optional[str]:
        """The URL to the Tibia.com page of the character with the highest bid, if applicable."""
        return get_character_url(self.highest_bidder) if self.highest_bidder is not None else None


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
    def url(self) -> str:
        """Get the URL to the houses section with the current parameters."""
        return get_houses_section_url(self.world, self.town, self.house_type, self.status, self.order)
