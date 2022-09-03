"""Models related to the houses section in Tibia.com."""
import datetime
import re
from typing import Dict, List, Optional

from tibiapy import abc
from tibiapy.enums import HouseOrder, HouseStatus, HouseType, Sex
from tibiapy.errors import InvalidContent
from tibiapy.utils import get_tibia_url, parse_form_data, parse_tibia_datetime, parse_tibia_money, \
    parse_tibiacom_content, parse_tibiacom_tables, try_date, try_datetime, try_enum

__all__ = (
    "HousesSection",
    "House",
    "CharacterHouse",
    "GuildHouse",
    "HouseEntry",
)

id_regex = re.compile(r'house_(\d+)\.')
bed_regex = re.compile(r'This (?P<type>\w+) can have up to (?P<beds>[\d-]+) bed')
info_regex = \
    re.compile(r'The house has a size of (?P<size>\d+) square meter[s]?. '
               r'The monthly rent is (?P<rent>\d+k?) gold and will be debited to the bank account on (?P<world>\w+).')

rented_regex = re.compile(r'The house has been rented by (?P<owner>[^.]+)\.'
                          r' (?P<pronoun>\w+) has paid the rent until (?P<paid_until>[^.]+)\.')
transfer_regex = re.compile(r'\w+ will move out on (?P<transfer_date>[^(]+)\([^)]+\)(?: and (?P<verb>wants to|will)'
                            r' pass the house to (?P<transferee>[\w\s]+) for (?P<transfer_price>\d+) gold coin)?')
moving_regex = re.compile(r'\w+ will move out on (?P<move_date>[^(]+)')
bid_regex = \
    re.compile(r'The highest bid so far is (?P<highest_bid>\d+) gold and has been submitted by (?P<bidder>[^.]+)')
auction_regex = re.compile(r'The auction (?P<auction_state>has ended|will end) at (?P<auction_end>[^.]+).')

list_header_regex = re.compile(r'Available (?P<type>[\w\s]+) in (?P<town>[\w\s\']+) on (?P<world>\w+)')
list_auction_regex = re.compile(r'\((?P<bid>\d+) gold; (?P<time_left>\w)+ (?P<time_unit>day|hour)s? left\)')


class HousesSection(abc.Serializable):
    """Represents the house section.

    .. versionadded:: 5.0.0

    Attributes
    ----------
    world: :class:`str`
        The selected world to show houses for.
    town: :class:`str`
        The town to show houses for.
    status: :class:`HouseStatus`
        The status to show. If :obj:`None`, any status is shown.
    house_type: :class:`HouseType`
        The type of houses to show.
    order: :class:`HouseOrder`
        The ordering to use for the results.
    entries: :class:`list` of :class:`HouseEntry`
        The houses matching the filters.
    available_worlds: :class:`list` of :class:`str`
        The list of available worlds to choose from.
    available_towns: :class:`list` of :class:`str`
        The list of available towns to choose from.
    """

    __slots__ = (
        "world",
        "town",
        "status",
        "house_type",
        "order",
        "entries",
        "available_worlds",
        "available_towns",
    )

    def __init__(self, **kwargs):
        self.world: str = kwargs.get("world")
        self.town: str = kwargs.get("town")
        self.status: Optional[HouseStatus] = kwargs.get("status")
        self.house_type: HouseType = kwargs.get("house_type")
        self.order: HouseOrder = kwargs.get("order", HouseOrder.NAME)
        self.available_worlds: List[str] = kwargs.get("available_worlds", [])
        self.available_towns: List[str] = kwargs.get("available_towns", [])
        self.entries: List[HouseEntry] = kwargs.get("entries", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} world={self.world!r} town={self.town!r} house_type={self.house_type!r}>"

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

    @classmethod
    def from_content(cls, content):
        """Parse the content of a house list from Tibia.com into a list of houses.

        Parameters
        ----------
        content: :class:`str`
            The raw HTML response from the house list.

        Returns
        -------
        :class:`HouseSection`
            The houses found in the page.

        Raises
        ------
        InvalidContent`
            Content is not the house list from Tibia.com
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            tables = parse_tibiacom_tables(parsed_content)
            house_results = cls()
            if "House Search" not in tables:
                raise InvalidContent("content does not belong to the houses section")
            form = parsed_content.select_one("div.BoxContent > form")
            house_results._parse_filters(form)
            if len(tables) < 2:
                return house_results
            houses_table = tables[list(tables.keys())[0]]
            _, *rows = houses_table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) != 5:
                    continue
                name = cols[0].text.replace('\u00a0', ' ')
                house = HouseEntry(name, house_results.world, 0, town=house_results.town,
                                   type=house_results.house_type)
                size = cols[1].text.replace('sqm', '')
                house.size = int(size)
                rent = cols[2].text.replace('gold', '')
                house.rent = parse_tibia_money(rent)
                status = cols[3].text.replace('\xa0', ' ')
                house._parse_status(status)
                id_input = cols[4].find("input", {'name': 'houseid'})
                house.id = int(id_input["value"])
                house_results.entries.append(house)
            return house_results
        except (ValueError, AttributeError, KeyError) as e:
            raise InvalidContent("content does not belong to a Tibia.com house list", e)

    def _parse_filters(self, form):
        form_data = parse_form_data(form)
        self.available_worlds = list(form_data["__options__"]["world"].values())
        self.available_towns = list(form_data["__options__"]["town"].values())
        self.world = form_data["world"]
        self.town = form_data["town"]
        self.status = try_enum(HouseStatus, form_data.get("state"))
        self.house_type = try_enum(HouseType, form_data.get("type", "")[:-1])
        self.order = try_enum(HouseOrder, form_data.get("order"), HouseOrder.NAME)
        return self


class House(abc.BaseHouse, abc.HouseWithId, abc.Serializable):
    """Represents a house in a specific world.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world the house belongs to.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of the house.
    image_url: :class:`str`
        The URL to the house's minimap image.
    beds: :class:`int`
        The number of beds the house has.
    size: :class:`int`
        The number of SQM the house has.
    rent: :class:`int`
        The monthly cost paid for the house, in gold coins.
    owner: :class:`str`
        The current owner of the house, if any.
    owner_sex: :class:`Sex`
        The sex of the owner of the house, if applicable.
    paid_until: :class:`datetime.datetime`, optional
        The date the last paid rent is due.
    transfer_date: :class:`datetime.datetime`, optional
        The date when the owner will move out of the house, if applicable.
    transferee: :class:`str`, optional
        The character who will receive the house when the owner moves, if applicable.
    transfer_price: :class:`int`
        The price that will be paid from the transferee to the owner for the house transfer.
    transfer_accepted: :class:`bool`
        Whether the house transfer has already been accepted or not.
    highest_bid: :class:`int`
        The currently highest bid on the house if it is being auctioned.
    highest_bidder: :class:`str`, optional
        The character that holds the highest bid.
    auction_end: :class:`datetime.datetime`, optional
        The date when the auction will end.
    """

    __slots__ = (
        "id",
        "name",
        "world",
        "status",
        "type",
        "image_url",
        "beds",
        "type",
        "size",
        "rent",
        "owner",
        "owner_sex",
        "paid_until",
        "transfer_date",
        "transferee",
        "transfer_price",
        "transfer_accepted",
        "highest_bid",
        "highest_bidder",
        "auction_end",
    )

    def __init__(self, name, world=None, **kwargs):
        self.id: int = kwargs.get("id", 0)
        self.name: str = name
        self.world: str = world
        self.image_url: str = kwargs.get("image_url")
        self.beds: int = kwargs.get("beds", 0)
        self.type: HouseType = try_enum(HouseType, kwargs.get("type"), HouseType.HOUSE)
        self.size: int = kwargs.get("size", 0)
        self.rent: int = kwargs.get("rent", 0)
        self.status: HouseStatus = try_enum(HouseStatus, kwargs.get("status"), None)
        self.owner: Optional[str] = kwargs.get("owner")
        self.owner_sex: Optional[str] = try_enum(Sex, kwargs.get("owner_sex"))
        self.paid_until: datetime.datetime = try_datetime(kwargs.get("paid_until"))
        self.transfer_date: datetime.datetime = try_datetime(kwargs.get("transfer_date"))
        self.transferee: Optional[str] = kwargs.get("transferee")
        self.transfer_price: int = kwargs.get("transfer_price", 0)
        self.transfer_accepted: bool = kwargs.get("transfer_accepted", False)
        self.highest_bid: int = kwargs.get("highest_bid", 0)
        self.highest_bidder: Optional[str] = kwargs.get("highest_bidder")
        self.auction_end: datetime.datetime = try_datetime(kwargs.get("auction_end"))

    # region Properties
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

    # endregion

    # region Public methods
    @classmethod
    def from_content(cls, content):
        """Parse a Tibia.com response into a House object.

        Parameters
        ----------
        content: :class:`str`
            HTML content of the page.

        Returns
        -------
        :class:`House`
            The house contained in the page, or None if the house doesn't exist.

        Raises
        ------
        InvalidContent
            If the content is not the house section on Tibia.com
        """
        try:
            parsed_content = parse_tibiacom_content(content)
            image_column, desc_column, *_ = parsed_content.find_all('td')
            if "Error" in image_column.text:
                return None
            image = image_column.find('img')
            for br in desc_column.find_all("br"):
                br.replace_with("\n")
            description = desc_column.text.replace("\u00a0", " ").replace("\n\n", "\n")
            lines = description.splitlines()
            try:
                name, beds, info, state, *_ = lines
            except ValueError:
                raise InvalidContent("content does is not from the house section of Tibia.com")

            house = cls(name.strip())
            house.image_url = image["src"]
            house.id = int(id_regex.search(house.image_url).group(1))
            m = bed_regex.search(beds)
            if m:
                if m.group("type").lower() in ["guildhall", "clanhall"]:
                    house.type = HouseType.GUILDHALL
                else:
                    house.type = HouseType.HOUSE
                house.beds = int(m.group("beds"))

            m = info_regex.search(info)
            if m:
                house.world = m.group("world")
                house.rent = parse_tibia_money(m.group("rent"))
                house.size = int(m.group("size"))

            house._parse_status(state)
            return house
        except (ValueError, TypeError) as e:
            raise InvalidContent("content does not belong to a house page", e)

    # endregion

    def _parse_status(self, status):
        """Parse the house's state description and applies the corresponding values.

        Parameters
        ----------
        status: :class:`str`
            Plain text string containing the current renting state of the house.
        """
        m = rented_regex.search(status)
        if m:
            self.status = HouseStatus.RENTED
            self.owner = m.group("owner")
            self.owner_sex = Sex.MALE if m.group("pronoun") == "He" else Sex.FEMALE
            self.paid_until = parse_tibia_datetime(m.group("paid_until"))
        else:
            self.status = HouseStatus.AUCTIONED

        m = transfer_regex.search(status)
        if m:
            self.transfer_date = parse_tibia_datetime(m.group("transfer_date"))
            self.transfer_accepted = m.group("verb") == "will"
            self.transferee = m.group("transferee")
            price = m.group("transfer_price")
            self.transfer_price = int(price) if price is not None else 0

        m = auction_regex.search(status)
        if m:
            self.auction_end = parse_tibia_datetime(m.group("auction_end"))

        m = bid_regex.search(status)
        if m:
            self.highest_bid = int(m.group("highest_bid"))
            self.highest_bidder = m.group("bidder")


class CharacterHouse(abc.BaseHouse, abc.HouseWithId, abc.Serializable):
    """A house owned by a character.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world the house belongs to.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of the house.
    town: :class:`str`
        The town where the city is located in.
    owner: :class:`str`
        The owner of the house.
    paid_until_date: :class:`datetime.date`
        The date the last paid rent is due.
    """

    __slots__ = (
        "id",
        "name",
        "world",
        "status",
        "type",
        "town",
        "owner",
        "paid_until_date",
    )

    def __init__(self, _id, name, world=None, town=None, owner=None, paid_until_date=None):
        self.id = int(_id)
        self.name: str = name
        self.town: str = town
        self.world: str = world
        self.owner: str = owner
        self.paid_until_date = try_date(paid_until_date)
        self.status = HouseStatus.RENTED
        self.type = HouseType.HOUSE


class GuildHouse(abc.BaseHouse, abc.Serializable):
    """A guildhall owned by a guild.

    By limitation of Tibia.com, the ID of the guildhall is not available.

    Attributes
    ----------
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world the house belongs to.
    status: :class:`HouseStatus`
        The current status of the house.

        This is kept for compatibility with house objects and will always be :obj:`HouseStatus.RENTED`.
    type: :class:`HouseType`
        The type of the house.

        This is kept for compatibility with house objects and will always be :obj:`HouseType.GUILDHALL`.
    owner: :class:`str`
        The owner of the guildhall.
    paid_until_date: :class:`datetime.date`
        The date the last paid rent is due.
    """

    __slots__ = (
        "name",
        "world",
        "status",
        "owner",
        "paid_until_date",
    )

    def __init__(self, name, world=None, owner=None, paid_until_date=None):
        self.name: str = name
        self.world: str = world
        self.owner: str = owner
        self.paid_until_date: datetime.date = try_date(paid_until_date)
        self.status: HouseStatus = HouseStatus.RENTED
        self.type: HouseType = HouseType.GUILDHALL

    def __repr__(self):
        return "<%s name=%r>" % (self.__class__.__name__, self.name)


class HouseEntry(abc.BaseHouse, abc.HouseWithId, abc.Serializable):
    """Represents a house from the house list in Tibia.com.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
    name: :class:`str`
        The name of the house.
    world: :class:`str`
        The name of the world the house belongs to.
    status: :class:`HouseStatus`
        The current status of the house.
    type: :class:`HouseType`
        The type of house.
    town: :class:`str`
        The town where the house is located.
    size: :class:`int`
        The size of the house in SQM.
    rent: :class:`int`
        The monthly cost of the house, in gold coins.
    time_left: :class:`datetime.timedelta`, optional
        The number of days or hours left until the bid ends, if it has started.
        This is not an exact measure, it is rounded to hours or days.
    highest_bid: :class:`int`, optional.
        The highest bid so far, if the auction has started.
    """

    __slots__ = (
        "id",
        "name",
        "world",
        "status",
        "type",
        "town",
        "size",
        "rent",
        "time_left",
        "highest_bid",
    )

    def __init__(self, name, world, houseid, **kwargs):
        self.name: str = name
        self.id = int(houseid)
        self.world: str = world
        self.status = try_enum(HouseStatus, kwargs.get("status"))
        self.type = try_enum(HouseType, kwargs.get("type"))
        self.town: str = kwargs.get("town")
        self.size: int = kwargs.get("size", 0)
        self.rent: int = kwargs.get("rent", 0)
        self.time_left: Optional[datetime.timedelta] = kwargs.get("time_left")
        self.highest_bid: Optional[int] = kwargs.get("highest_bid", None)

    # region Private methods
    def _parse_status(self, status):
        """
        Parse the status string found in the table and applies the corresponding values.

        Parameters
        ----------
        status: :class:`str`
            The string containing the status.
        """
        if "rented" in status:
            self.status = HouseStatus.RENTED
        else:
            m = list_auction_regex.search(status)
            if m:
                self.highest_bid = int(m.group('bid'))
                if m.group("time_unit") == "day":
                    self.time_left = datetime.timedelta(days=int(m.group("time_left")))
                else:
                    self.time_left = datetime.timedelta(hours=int(m.group("time_left")))
            self.status = HouseStatus.AUCTIONED
    # endregion
