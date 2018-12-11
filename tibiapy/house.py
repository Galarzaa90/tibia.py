import re

import bs4

from tibiapy import abc
from tibiapy.utils import parse_number_words, parse_tibia_datetime

URL_HOUSE = "https://www.tibia.com/community/?subtopic=houses&page=view&houseid=%d&world=%s"
URL_HOUSE_TIBIADATA = "https://api.tibiadata.com/v2/house/%s/%d.json"

id_regex = re.compile(r'house_(\d+)\.')
bed_regex = re.compile(r'This (?P<type>\w+) has (?P<beds>[\w-]+) bed')
info_regex = re.compile(r'The house has a size of (?P<size>\d+) square meter[s]?. The monthly rent is (?P<rent>\d+) gold and will be debited to the bank account on (?P<world>\w+).')

rented_regex = re.compile(r'The house has been rented by (?P<owner>[^.]+)\. (?P<pronoun>\w+) has paid the rent until (?P<paid_until>[^.]+)\.')
transfer_regex = re.compile(r'\w+ will move out on (?P<transfer_date>[^(]+)\([^)]+\)(?: and (?P<verb>wants to|will) pass the house to (?P<transferee>[\w\s]+) for (?P<transfer_price>\d+) gold coin)?')
moving_regex = re.compile(r'\w+ will move out on (?P<move_date>[^(]+)')
bid_regex = re.compile(r'The highest bid so far is (?P<highest_bid>\d+) gold and has been submitted by (?P<bidder>[^.]+)')
auction_regex = re.compile(r'The auction (?P<auction_state>has ended|will end) at (?P<auction_end>[^.]+).')

class House(abc.Serializable):
    """Represents a house in a specific world.

    Attributes
    ----------
    name: :class:`str`
        The name of the house.
    id: :class:`int`
        The internal ID of the house. This is used on the website to identify houses.
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
    state: :class:`str`
        The renting state of the house, can be ``rented`` or ``auctioned``.
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
    __slots__ = ("name", "id", "world", "image_url", "beds", "type", "size", "rent", "state", "owner", "owner_sex",
                 "paid_until", "transfer_date", "transferee", "transfer_price", "transfer_accepted", "highest_bid",
                 "highest_bidder", "auction_end")

    def __init__(self, name, world=None, **kwargs):
        self.name = name
        self.world = world
        self.image_url = kwargs.get("image_url")
        self.beds = kwargs.get("beds", 0)
        self.type = kwargs.get("type", "house")
        self.size = kwargs.get("size", 0)
        self.rent = kwargs.get("rent", 0)
        self.state = kwargs.get("state")
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
    def url(self):
        """:class:`str`: The URL to the Tibia.com page of the house."""
        return self.get_url(self.id, self.world) if self.id and self.world else None

    @property
    def url_tibiadata(self):
        """:class:`str`: The URL to the TibiaData.com page of the house."""
        return self.get_url_tibiadata(self.id, self.world) if self.id and self.world else None

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
            house.type = "guildhall" if m.group("type") in ["guildhall", "clanhall"] else "house"
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

        m = rented_regex.search(state)
        if m:
            house.state = "rented"
            house.owner = m.group("owner")
            house.owner_sex = "male" if m.group("pronoun") == "He" else "female"
            house.paid_until = parse_tibia_datetime(m.group("paid_until"))
        else:
            house.state = "auctioned"

        m = transfer_regex.search(state)
        if m:
            house.transfer_date = parse_tibia_datetime(m.group("transfer_date"))
            house.transfer_accepted = m.group("verb") == "will"
            house.transferee = m.group("transferee")
            price = m.group("transfer_price")
            house.transfer_price = int(price) if price is not None else 0

        m = auction_regex.search(state)
        if m:
            house.auction_end = parse_tibia_datetime(m.group("auction_end"))

        m = bid_regex.search(state)
        if m:
            house.highest_bid = int(m.group("highest_bid"))
            house.highest_bidder = m.group("bidder")

        print(house.to_json(indent=2))
        return house


    @classmethod
    def get_url(cls, house_id, world):
        """ Gets the Tibia.com URL for house with the given id and world.

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
        return URL_HOUSE % (house_id, world)

    @classmethod
    def get_url_tibiadata(cls, house_id, world):
        """ Gets the TibiaData.com URL for house with the given id and world.

        Parameters
        ----------
        house_id: :class:`int`
            The internal id of the house.
        world: :class:`str`
            The world of the house.

        Returns
        -------
        The URL to the house in TibiaData.com
        """
        return URL_HOUSE % (world, house_id)