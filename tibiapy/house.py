import json
import re

import bs4

import tibiapy.character
from tibiapy import abc
from tibiapy.enums import HouseStatus, HouseType, Sex, try_enum
from tibiapy.utils import parse_number_words, parse_tibia_datetime

id_regex = re.compile(r'house_(\d+)\.')
bed_regex = re.compile(r'This (?P<type>\w+) has (?P<beds>[\w-]+) bed')
info_regex = re.compile(r'The house has a size of (?P<size>\d+) square meter[s]?. The monthly rent is (?P<rent>\d+) gold and will be debited to the bank account on (?P<world>\w+).')

rented_regex = re.compile(r'The house has been rented by (?P<owner>[^.]+)\. (?P<pronoun>\w+) has paid the rent until (?P<paid_until>[^.]+)\.')
transfer_regex = re.compile(r'\w+ will move out on (?P<transfer_date>[^(]+)\([^)]+\)(?: and (?P<verb>wants to|will) pass the house to (?P<transferee>[\w\s]+) for (?P<transfer_price>\d+) gold coin)?')
moving_regex = re.compile(r'\w+ will move out on (?P<move_date>[^(]+)')
bid_regex = re.compile(r'The highest bid so far is (?P<highest_bid>\d+) gold and has been submitted by (?P<bidder>[^.]+)')
auction_regex = re.compile(r'The auction (?P<auction_state>has ended|will end) at (?P<auction_end>[^.]+).')


class House(abc.HouseWithId):
    """Represents a house in a specific world.

    Attributes
    ----------
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
    name: :class:`str`
        The name of the house.
    image_url: :class:`str`
        The URL to the house's minimap image.
    beds: :class:`int`
        The number of beds the house has.
    type: :class:`str`
        The type of house. It can be a regular ``house`` or a ``guildhall``.
    size: :class:`int`
        The number of SQM the house has.
    rent: :class:`int`
        The monthly rent paid for the house.
    world: :class:`str`
        The world of the house.
    status: :class:`str`
        The renting status of the house, can be ``rented`` or ``auctioned``.
    owner: :class:`str`
        The current owner of the house, if any.
    owner_sex: :class:`str`
        The sex of the owner of the house, if applicable.
    paid_until: :class:`datetime.datetime`
        The date the last paid rent is due.
    transfer_date: :class:`datetime.datetime`
        The date when the owner will move out of the house, if applicable.
    transferee: :class:`str`
        The character who will receive the house when the owner moves, if applicable.
    transfer_price: :class:`int`
        The price that will be paid from the transferee to the owner for the house transfer.
    transfer_accepted: :class:`bool`
        Whether the house transfer has already been accepted or not.
    highest_bid: :class:`int`
        The currently highest bid on the house if it is being auctioned.
    highest_bidder: :class:`str`
        The character that holds the highest bid.
    auction_end: :class:`datetime.datetime`
        The date where the auction will end.
    """
    __slots__ = ("id", "image_url", "beds", "type", "size", "rent", "owner", "owner_sex",
                 "paid_until", "transfer_date", "transferee", "transfer_price", "transfer_accepted", "highest_bid",
                 "highest_bidder", "auction_end")

    def __init__(self, name, world=None, **kwargs):
        self.name = name
        self.world = world
        self.image_url = kwargs.get("image_url")
        self.beds = kwargs.get("beds", 0)
        self.type = kwargs.get("type", HouseType.HOUSE)
        self.size = kwargs.get("size", 0)
        self.rent = kwargs.get("rent", 0)
        self.status = kwargs.get("status")
        self.owner = kwargs.get("owner")
        self.owner_sex = kwargs.get("owner_sex")
        self.paid_until = kwargs.get("paid_until")
        self.transfer_date = kwargs.get("transfer_date")
        self.transferee = kwargs.get("transferee")
        self.transfer_price = kwargs.get("transfer_price", 0)
        self.transfer_accepted = kwargs.get("transfer_accepted", False)
        self.highest_bid = kwargs.get("highest_bid", 0)
        self.highest_bidder = kwargs.get("highest_bidder")

    @property
    def owner_url(self):
        """:class:`str`: The URL to the Tibia.com page of the house's owner, if applicable."""
        return tibiapy.Character.get_url(self.owner) if self.owner is not None else None

    @property
    def transferee_url(self):
        """:class:`str`: The URL to the Tibia.com page of the character receiving the house, if applicable."""
        return tibiapy.Character.get_url(self.transferee) if self.transferee is not None else None


    @classmethod
    def from_content(cls, content):
        """Parses a Tibia.com response into a House object.

        Parameters
        ----------
        content: :class:`str`
            HTML content of the page.

        Returns
        -------
        :class:`House`
            The house contained in the page, or None if the house doesn't exist.
        """
        parsed_content = bs4.BeautifulSoup(content.replace('ISO-8859-1', 'utf-8'), 'lxml',
                                           parse_only=bs4.SoupStrainer("div", class_="BoxContent"))
        image_column, desc_column, *_ = parsed_content.find_all('td')
        if "Error" in image_column:
            return None
        image = image_column.find('img')
        if image is None:
            return None
        for br in desc_column.find_all("br"):
            br.replace_with("\n")
        description = desc_column.text.replace("\u00a0", " ").replace("\n\n","\n")
        lines = description.splitlines()
        name, beds, info, state, *_ = lines

        house = cls(name.strip())
        house.image_url = image["src"]
        house.id = int(id_regex.search(house.image_url).group(1))
        m = bed_regex.search(beds)
        if m:
            house.type = HouseType.GUILDHALL if m.group("type") in ["guildhall", "clanhall"] else HouseType.HOUSE
            beds_word = m.group("beds")
            if beds_word == "no":
                house.beds = 0
            else:
                house.beds = parse_number_words(beds_word)

        m = info_regex.search(info)
        if m:
            house.world = m.group("world")
            house.rent = int(m.group("rent"))
            house.size = int(m.group("size"))

        house._parse_status(state)
        return house

    @classmethod
    def from_tibiadata(cls, content):
        """
        Parses a TibiaData response into a House object.
        Parameters
        ----------
        content: :class:`str`
            The JSON content of the TibiaData response.

        Returns
        -------
        :class:`House`
            The house contained in the response, if found.
        """
        try:
            json_content = json.loads(content)
        except json.JSONDecodeError:
            return None
        try:
            house_json = json_content["house"]
            if not house_json["name"]:
                return None
            house = cls(house_json["name"], house_json["world"])

            house.type = try_enum(HouseType, house_json["type"])
            house.beds = house_json["beds"]
            house.size = house_json["size"]
            house.size = house_json["size"]
            house.rent = house_json["rent"]
            house.image_url = house_json["img"]

            # Parsing the original status string is easier than dealing with TibiaData fields
            house._parse_status(house_json["status"]["original"])
        except KeyError:
            return None
        return house

    def _parse_status(self, status):
        """Parses the house's state description and applies the corresponding values

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


class CharacterHouse(abc.HouseWithId):
    __slots__ = ("town", "owner", "paid_until_date")

    def __init__(self, _id, name, town=None, owner=None, paid_until_date=None):
        self.id = _id
        self.name = name
        self.town = town
        self.owner = owner
        self.paid_until_date = paid_until_date
        self.status = HouseStatus.RENTED
        self.type = HouseType.HOUSE


class GuildHouse(abc.House):
    __slots__ = ("owner", "paid_until_date")

    def __init__(self, name, town=None, owner=None, paid_until_date=None):
        self.name = name
        self.town = town
        self.owner = owner
        self.paid_until_date = paid_until_date
        self.status = HouseStatus.RENTED
        self.type = HouseType.GUILDHALL
