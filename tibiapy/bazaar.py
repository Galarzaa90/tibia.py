"""Contains all classes related to the Character Bazaar sections in Tibia.com"""
import datetime
import logging
import re
import urllib.parse
from typing import Dict, List, Optional

import bs4

from tibiapy import InvalidContent, Sex, Vocation, abc
from tibiapy.abc import BaseCharacter
from tibiapy.enums import (AuctionOrder, AuctionOrderBy, AuctionSearchType, AuctionStatus, BattlEyeTypeFilter,
                           BazaarType, BidType, PvpTypeFilter, SkillFilter, VocationAuctionFilter)
from tibiapy.utils import (convert_line_breaks, get_tibia_url, parse_form_data, parse_integer, parse_pagination,
                           parse_tibia_datetime, parse_tibiacom_content, try_enum)

__all__ = (
    "AchievementEntry",
    "Auction",
    "AuctionFilters",
    "CharacterBazaar",
    "CharmEntry",
    "BestiaryEntry",
    "BlessingEntry",
    "DisplayItem",
    "DisplayMount",
    "DisplayOutfit",
    "DisplayFamiliar",
    "ItemSummary",
    "AuctionEntry",
    "Outfits",
    "OutfitImage",
    "Mounts",
    "Familiars",
    "SalesArgument",
    "SkillEntry",
)

results_pattern = re.compile(r'Results: (\d+)')
char_info_regex = re.compile(r'Level: (\d+) \| Vocation: ([\w\s]+)\| (\w+) \| World: (\w+)')
id_addon_regex = re.compile(r'(\d+)_(\d)\.gif')
id_regex = re.compile(r'(\d+).(?:gif|png)')
description_regex = re.compile(r'"(?:an?\s)?([^"]+)"')
amount_regex = re.compile(r'([\d,]+)x')
tier_regex = re.compile(r"(.*)\s\(tier (\d)\)")

log = logging.getLogger("tibiapy")


class AchievementEntry(abc.Serializable):
    """An unlocked achievement by the character.

    Attributes
    ----------
    name: :class:`str`
        The name of the achievement.
    secret: :class:`bool`
        Whether the achievement is secret or not.
    """

    def __init__(self, name, secret=False):
        self.name: str = name
        self.secret: int = secret

    __slots__ = (
        "name",
        "secret",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} secret={self.secret}>"


class AuctionFilters(abc.Serializable):
    """The auction filters available in the auctions section.

    All attributes are optional.

    Attributes
    ----------
    world: :class:`str`
        The character's world to show characters for.
    pvp_type: :class:`PvpTypeFilter`
        The PvP type of the character's worlds to show.
    battleye: :class:`BattlEyeTypeFilter`
        The type of BattlEye protection of the character's worlds to show.
    vocation: :class:`VocationAuctionFilter`
        The character vocation to show results for.
    min_level: :class:`int`
        The minimum level to display.
    max_level: :class:`int`
        The maximum level to display.
    skill: :class:`SkillFilter`
        The skill to filter by its level range.
    min_skill_level: :class:`int`
        The minimum skill level of the selected :attr:`skill` to display.
    max_skill_level: :class:`int`
        The maximum skill level of the selected :attr:`skill` to display.
    search_string: :class:`str`
        The search term to filter out auctions.
    search_type: :class:`AuctionSearchType`
        The type of search to use. Defines the behaviour of :py:attr:`search_string`.
    available_worlds: :class:`list` of :class:`str`
        The list of available worlds to select to filter.
    """

    __slots__ = (
        "world",
        "pvp_type",
        "battleye",
        "vocation",
        "min_level",
        "max_level",
        "skill",
        "min_skill_level",
        "max_skill_level",
        "order_by",
        "order",
        "search_string",
        "search_type",
        "available_worlds",
    )

    def __init__(self, **kwargs):
        self.world: Optional[str] = kwargs.get("world")
        self.pvp_type: Optional[PvpTypeFilter] = kwargs.get("pvp_type")
        self.battleye: Optional[BattlEyeTypeFilter] = kwargs.get("battleye")
        self.vocation: Optional[VocationAuctionFilter] = kwargs.get("vocation")
        self.min_level: Optional[int] = kwargs.get("min_level")
        self.max_level: Optional[int] = kwargs.get("max_level")
        self.skill: Optional[SkillFilter] = kwargs.get("skill")
        self.min_skill_level: Optional[int] = kwargs.get("min_skill_level")
        self.max_skill_level: Optional[int] = kwargs.get("max_skill_level")
        self.order_by: Optional[AuctionOrderBy] = kwargs.get("order_by")
        self.order: Optional[AuctionOrder] = kwargs.get("order")
        self.search_string: Optional[str] = kwargs.get("search_string")
        self.search_type: Optional[AuctionSearchType] = kwargs.get("search_type")
        self.available_worlds: List[str] = kwargs.get("available_worlds", [])

    def __repr__(self):
        attributes = ""
        for attr in self.__slots__:
            v = getattr(self, attr)
            attributes += f" {attr}={v!r}"
        return f"<{self.__class__.__name__}{attributes}>"

    @property
    def query_params(self):
        """:class:`dict`: The query parameters representing this filter."""
        params = {
            "filter_profession": self.vocation.value if self.vocation else None,
            "filter_levelrangefrom": self.min_level,
            "filter_levelrangeto": self.max_level,
            "filter_world": self.world,
            "filter_worldpvptype": self.pvp_type.value if self.pvp_type else None,
            "filter_worldbattleyestate": self.battleye.value if self.battleye else None,
            "filter_skillid": self.skill.value if self.skill else None,
            "filter_skillrangefrom": self.min_skill_level,
            "filter_skillrangeto": self.max_skill_level,
            "order_column": self.order_by.value if self.order_by else None,
            "order_direction": self.order.value if self.order else None,
            "searchstring": self.search_string,
            "searchtype": self.search_type.value if self.search_type else None,
        }
        return {k: v for k, v in params.items() if v is not None}

    @classmethod
    def _parse_filter_table(cls, table):
        """Parse the filters table to extract its values.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the filters.

        Returns
        -------
        :class:`AuctionFilters`
            The currently applied filters.
        """
        filters = AuctionFilters()
        forms = table.find_all("form")
        data = parse_form_data(forms[0], include_options=True)

        filters.world = data["filter_world"]
        filters.available_worlds = [w for w in data.get("__options__", {}).get("filter_world", []) if "(" not in w]
        filters.pvp_type = try_enum(PvpTypeFilter, parse_integer(data.get("filter_worldpvptype"), None))
        filters.battleye = try_enum(BattlEyeTypeFilter, parse_integer(data.get("filter_worldbattleyestate"), None))
        filters.vocation = try_enum(VocationAuctionFilter, parse_integer(data.get("filter_profession"), None))
        filters.min_level = parse_integer(data.get("filter_levelrangefrom"), None)
        filters.max_level = parse_integer(data.get("filter_levelrangeto"), None)
        filters.skill = try_enum(SkillFilter, parse_integer(data.get("filter_skillid"), None))
        filters.min_skill_level = parse_integer(data.get("filter_skillrangefrom"), None)
        filters.max_skill_level = parse_integer(data.get("filter_skillrangeto"), None)
        filters.order_by = try_enum(AuctionOrderBy, parse_integer(data.get("order_column"), None))
        filters.order = try_enum(AuctionOrder, parse_integer(data.get("order_direction"), None))
        if len(forms) > 1:
            data_search = parse_form_data(forms[1], include_options=True)
            filters.search_string = data_search.get("searchstring")
            filters.search_type = try_enum(AuctionSearchType, parse_integer(data_search.get("searchtype"), None))
        return filters


class BestiaryEntry(abc.Serializable):
    """The bestiary progress for a specific creature.

    Attributes
    ----------
    name: :class:`str`
        The name of the creature.
    kills: :class:`int`
        The number of kills of this creature the player has done.
    step: :class:`int`
        The current step to unlock this creature the character is in, where 4 is fully unlocked.
    """

    def __init__(self, name, kills, step):
        self.name: str = name
        self.kills: int = kills
        self.step: int = step

    __slots__ = (
        "name",
        "kills",
        "step",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} kills={self.kills} step={self.step}>"

    @property
    def completed(self):
        """:class:`bool`: Whether the entry is completed or not."""
        return self.step == 4


class BlessingEntry(abc.Serializable):
    """A character's blessings.

    Attributes
    ----------
    name: :class:`str`
        The name of the blessing.
    amount: :class:`int`
        The amount of blessing charges the character has.
    """

    __slots__ = (
        "name",
        "amount",
    )

    def __init__(self, name, amount=0):
        self.name: str = name
        self.amount: int = amount

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} amount={self.amount}>"


class CharacterBazaar(abc.Serializable):
    """Represents the char bazaar.

    Attributes
    ----------
    page: :class:`int`
        The page being currently viewed.
    total_pages: :class:`int`
        The total number of pages available.
    results_count: :class:`int`
        The number of auctions listed.
    entries: :class:`list` of :class:`AuctionEntry`
        The auctions displayed.
    type: :class:`BazaarType`
        The type of auctions being displayed, either current or auction history.
    filters: :class:`AuctionFilters`
        The currently set filtering options.
    """

    __slots__ = (
        "type",
        "filters",
        "page",
        "total_pages",
        "results_count",
        "entries",
    )

    def __init__(self, **kwargs):
        self.type: BazaarType = kwargs.get("type")
        self.filters: Optional[AuctionFilters] = kwargs.get("filters")
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.results_count: int = kwargs.get("results_count", 0)
        self.entries: List[AuctionEntry] = kwargs.get("entries", [])

    def __repr__(self):
        return f"<{self.__class__.__name__} page={self.page} total_pages={self.total_pages} " \
               f"results_count={self.results_count}>"

    # region Properties
    @property
    def url(self):
        """:class:`str`: Get the URL to the bazaar."""
        return self.get_auctions_history_url(self.page) if self.type == BazaarType.HISTORY else \
            self.get_current_auctions_url(self.page, self.filters)
    # endregion

    # region Public Methods
    @classmethod
    def get_current_auctions_url(cls, page=1, filters=None):
        """Get the URL to the list of current auctions in Tibia.com.

        Parameters
        ----------
        page: :class:`int`
            The page to show the URL for.
        filters: :class:`AuctionFilters`
            The filtering criteria to use.

        Returns
        -------
        :class:`str`
            The URL to the current auctions section in Tibia.com
        """
        filters = filters or AuctionFilters()
        return get_tibia_url("charactertrade", "currentcharactertrades", currentpage=page, **filters.query_params)

    @classmethod
    def get_auctions_history_url(cls, page=1, filters=None):
        """Get the URL to the auction history in Tibia.com.

        Parameters
        ----------
        page: :class:`int`
            The page to show the URL for.
        filters: :class:`AuctionFilters`
            The filtering criteria to use.

        Returns
        -------
        :class:`str`
            The URL to the auction history section in Tibia.com
        """
        filters = filters or AuctionFilters()
        return get_tibia_url("charactertrade", "pastcharactertrades", currentpage=page, **filters.query_params)

    @classmethod
    def from_content(cls, content):
        """Get the bazaar's information and list of auctions from Tibia.com.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the bazaar section at Tibia.com.

        Returns
        -------
        :class:`CharacterBazaar`
            The character bazaar with the entries found.
        """
        try:
            parsed_content = parse_tibiacom_content(content, builder='html5lib')
            content_table = parsed_content.find("div", attrs={"class": "BoxContent"})
            tables = content_table.find_all("div", attrs={"class": "TableContainer"})
            filter_table = None
            if len(tables) == 1:
                auctions_table = tables[0]
            else:
                filter_table, auctions_table, *_ = tables

            bazaar = cls()
            bazaar.type = BazaarType.CURRENT if filter_table else BazaarType.HISTORY

            if filter_table:
                bazaar.filters = AuctionFilters._parse_filter_table(filter_table)

            page_navigation_row = parsed_content.find("td", attrs={"class": "PageNavigation"})
            if page_navigation_row:
                bazaar.page, bazaar.total_pages, bazaar.results_count = parse_pagination(page_navigation_row)

            auction_rows = auctions_table.find_all("div", attrs={"class": "Auction"})
            for auction_row in auction_rows:
                auction = AuctionEntry._parse_auction(auction_row)

                bazaar.entries.append(auction)
            return bazaar
        except (ValueError, IndexError) as e:
            raise InvalidContent("content does not belong to the bazaar at Tibia.com", original=e)
    # endregion


class CharmEntry(abc.Serializable):
    """An unlocked charm by the character.

    Attributes
    ----------
    name: :class:`str`
        The name of the charm.
    cost: :class:`int`
        The cost of the charm in charm points.
    """

    def __init__(self, name, cost=0):
        self.name: str = name
        self.cost: int = cost

    __slots__ = (
        "name",
        "cost",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} cost={self.cost}>"


class DisplayImage(abc.Serializable):
    """An image displayed in the auction.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the image.
    name: :class:`str`
        The element's name.
    """

    def __init__(self, **kwargs):
        self.image_url: str = kwargs.get("image_url")
        self.name: str = kwargs.get("name")

    __slots__ = (
        "image_url",
        "name",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} image_url={self.image_url!r}>"

    @classmethod
    def _parse_image_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.find("img")
        if not img_tag:
            return None
        return cls(image_url=img_tag["src"], name=description)


class DisplayItem(abc.Serializable):
    """Represents an item displayed on an auction, or the character's items in the auction detail.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the item's image.
    name: :class:`str`
        The item's name.
    description: :class:`str`
        The item's description, if any.
    count: :class:`int`
        The item's count.
    item_id: :class:`int`
        The item's client id.
    tier: :class:`int`
        The item's tier.
    """

    __slots__ = (
        "image_url",
        "name",
        "description",
        "count",
        "item_id",
        "tier",
    )

    def __init__(self, **kwargs):
        self.image_url: str = kwargs.get("image_url")
        self.name: str = kwargs.get("name")
        self.description: str = kwargs.get("description")
        self.count: int = kwargs.get("count", 1)
        self.item_id: int = kwargs.get("item_id", 0)
        self.tier: int = kwargs.get("tier", 0)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} count={self.count} item_id={self.item_id}>"

    @classmethod
    def _parse_image_box(cls, item_box):
        title_text = item_box["title"]
        img_tag = item_box.find("img")
        if not img_tag:
            return None
        m = amount_regex.match(title_text)
        amount = 1
        if m:
            amount = parse_integer(m.group(1))
            title_text = amount_regex.sub("", title_text, 1).strip()
        item_id = 0
        description = None
        name, *desc = title_text.split("\n")
        if desc:
            description = " ".join(desc)
        tier = 0
        m = tier_regex.search(name)
        if m:
            tier = int(m.group(2))
            name = m.group(1)
        m = id_regex.search(img_tag["src"])
        if m:
            item_id = int(m.group(1))
        return DisplayItem(image_url=img_tag["src"], name=name, count=amount, item_id=item_id, description=description,
                           tier=tier)


class DisplayMount(DisplayImage):
    """Represents a mount owned or unlocked by the character.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the image.
    name: :class:`str`
        The mount's name.
    mount_id: :class:`int`
        The internal ID of the mount.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mount_id: int = kwargs.get("mount_id", 0)

    __slots__ = (
        "mount_id",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} mount_id={self.mount_id} image_url={self.image_url!r}>"

    @classmethod
    def _parse_image_box(cls, item_box):
        mount = super()._parse_image_box(item_box)
        m = id_regex.search(mount.image_url)
        if m:
            mount.mount_id = int(m.group(1))
        return mount


class DisplayOutfit(DisplayImage):
    """Represents an outfit owned or unlocked by the character.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the image.
    name: :class:`str`
        The outfit's name.
    outfit_id: :class:`int`
        The internal ID of the outfit.
    addons: :class:`int`
        The unlocked or owned addons for this outfit.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outfit_id: int = kwargs.get("outfit_id", 0)
        self.addons: int = kwargs.get("addons", 0)

    __slots__ = (
        "outfit_id",
        "addons",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} outfit_id={self.outfit_id} addons={self.addons} " \
               f"image_url={self.image_url!r}>"

    @classmethod
    def _parse_image_box(cls, item_box):
        outfit = super()._parse_image_box(item_box)
        name = outfit.name.split("(")[0].strip()
        outfit.name = name
        m = id_addon_regex.search(outfit.image_url)
        if m:
            outfit.outfit_id = int(m.group(1))
            outfit.addons = int(m.group(2))
        return outfit


class DisplayFamiliar(DisplayImage):
    """Represents a familiar owned or unlocked by the character.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the image.
    name: :class:`str`
        The familiar's name.
    familiar_id: :class:`int`
        The internal ID of the familiar.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.familiar_id: int = kwargs.get("familiar_id", 0)

    __slots__ = (
        "familiar_id",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} familiar_id={self.familiar_id} " \
               f"image_url={self.image_url!r}>"

    @classmethod
    def _parse_image_box(cls, item_box):
        familiar = super()._parse_image_box(item_box)
        name = familiar.name.split("(")[0].strip()
        familiar.name = name
        m = id_regex.search(familiar.image_url)
        if m:
            familiar.familiar_id = int(m.group(1))
        return familiar


class AuctionEntry(BaseCharacter, abc.Serializable):
    """Represents an auction in the list, containing the summary.

    Attributes
    ----------
    auction_id: :class:`int`
        The internal id of the auction.
    name: :class:`str`
        The name of the character.
    level: :class:`int`
        The level of the character.
    world: :class:`str`
        The world the character is in.
    vocation: :class:`Vocation`
        The vocation of the character.
    sex: :class:`Sex`
        The sex of the character.
    outfit: :class:`OutfitImage`
        The current outfit selected by the user.
    displayed_items: :class:`list` of :class:`DisplayItem`
        The items selected to be displayed.
    sales_arguments: :class:`list` of :class:`SalesArgument`
        The sale arguments selected for the auction.
    auction_start: :class:`datetime.datetime`
        The date when the auction started.
    auction_end: :class:`datetime.datetime`
        The date when the auction ends.
    bid: :class:`int`
        The current bid in Tibia Coins.
    bid_type: :class:`BidType`
        The type of the auction's bid.
    status: :class:`AuctionStatus`
        The current status of the auction.
    """

    __slots__ = (
        "auction_id",
        "name",
        "level",
        "world",
        "vocation",
        "sex",
        "outfit",
        "displayed_items",
        "sales_arguments",
        "auction_start",
        "auction_end",
        "bid",
        "bid_type",
        "status",
    )

    def __init__(self, **kwargs):
        self.auction_id: int = kwargs.get("auction_id", 0)
        self.name: str = kwargs.get("name")
        self.level: int = kwargs.get("level", 0)
        self.world: str = kwargs.get("world")
        self.vocation: Vocation = kwargs.get("vocation")
        self.sex: Sex = kwargs.get("sex")
        self.outfit: OutfitImage = kwargs.get("outfit")
        self.displayed_items: List[DisplayItem] = kwargs.get("displayed_items", [])
        self.sales_arguments: List[SalesArgument] = kwargs.get("sales_arguments", [])
        self.auction_start: datetime.datetime = kwargs.get("auction_start")
        self.auction_end: datetime.datetime = kwargs.get("auction_end")
        self.bid: int = kwargs.get("bid", 0)
        self.bid_type: BidType = kwargs.get("bid_type")
        self.status: AuctionStatus = kwargs.get("status")

    def __repr__(self):
        return f"<{self.__class__.__name__} auction_id={self.auction_id} name={self.name!r} world={self.world!r}>"

    # region Properties
    @property
    def character_url(self):
        """:class:`str`: The URL of the character's information page on Tibia.com."""
        return BaseCharacter.get_url(self.name)

    @property
    def url(self):
        """:class:`str`: The URL to this auction's detail page on Tibia.com."""
        return self.get_url(self.auction_id)
    # endregion

    # region Public Methods
    @classmethod
    def get_url(cls, auction_id):
        """Get the URL to the Tibia.com detail page of an auction with a given id.

        Parameters
        ----------
        auction_id: :class:`int`
            The ID of the auction.

        Returns
        -------
        :class:`str`
            The URL to the auction's detail page.
        """
        return get_tibia_url("charactertrade", "currentcharactertrades", page="details", auctionid=auction_id)
    # endregion

    # region Private Methods
    @classmethod
    def _parse_auction(cls, auction_row, auction_id=0):
        """Parse an auction's table, extracting its data.

        Parameters
        ----------
        auction_row: :class:`bs4.Tag`
            The row containing the auction's information.
        auction_id: :class:`int`
            The ID of the auction.

        Returns
        -------
        :class:`AuctionEntry`
            The auction contained in the table.
        """
        header_container = auction_row.find("div", attrs={"class": "AuctionHeader"})
        char_name_container = header_container.find("div", attrs={"class": "AuctionCharacterName"})
        char_link = char_name_container.find("a")
        if char_link:
            url = urllib.parse.urlparse(char_link["href"])
            query = urllib.parse.parse_qs(url.query)
            auction_id = int(query["auctionid"][0])
            name = char_link.text
        else:
            name = char_name_container.text

        auction = cls(name=name, auction_id=auction_id)
        char_name_container.replaceWith('')
        m = char_info_regex.search(header_container.text)
        if m:
            auction.level = int(m.group(1))
            auction.vocation = try_enum(Vocation, m.group(2).strip())
            auction.sex = try_enum(Sex, m.group(3).strip().lower())
            auction.world = m.group(4)
        outfit_img = auction_row.find("img", {"class": "AuctionOutfitImage"})
        m = id_addon_regex.search(outfit_img["src"])
        if m:
            auction.outfit = OutfitImage(image_url=outfit_img["src"], outfit_id=int(m.group(1)), addons=int(m.group(2)))
        item_boxes = auction_row.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayItem._parse_image_box(item_box)
            if item:
                auction.displayed_items.append(item)
        dates_containers = auction_row.find("div", {"class": "ShortAuctionData"})
        start_date_tag, end_date_tag, *_ = dates_containers.find_all("div", {"class": "ShortAuctionDataValue"})
        auction.auction_start = parse_tibia_datetime(start_date_tag.text.replace('\xa0', ' '))
        auction.auction_end = parse_tibia_datetime(end_date_tag.text.replace('\xa0', ' '))
        bids_container = auction_row.find("div", {"class": "ShortAuctionDataBidRow"})
        bid_tag = bids_container.find("div", {"class", "ShortAuctionDataValue"})
        bid_type_tag = bids_container.find_all("div", {"class", "ShortAuctionDataLabel"})[0]
        bid_type_str = bid_type_tag.text.replace(":", "").strip()
        auction.bid_type = try_enum(BidType, bid_type_str)
        auction.bid = parse_integer(bid_tag.text)
        auction_body_block = auction_row.find("div", {"class", "CurrentBid"})
        auction_info_tag = auction_body_block.find("div", {"class": "AuctionInfo"})
        status = ""
        if auction_info_tag:
            convert_line_breaks(auction_info_tag)
            status = auction_info_tag.text.replace("\n", " ").replace("  ", " ")
        auction.status = try_enum(AuctionStatus, status, AuctionStatus.IN_PROGRESS)
        argument_entries = auction_row.find_all("div", {"class": "Entry"})
        for entry in argument_entries:
            img = entry.find("img")
            img_url = img["src"]
            category_id = 0
            m = id_regex.search(img_url)
            if m:
                category_id = parse_integer(m.group(1))
            auction.sales_arguments.append(SalesArgument(content=entry.text, category_image=img_url,
                                                         category_id=category_id))
        return auction
    # endregion


class Auction(AuctionEntry):
    """The details of an auction.

    Attributes
    ----------
    auction_id: :class:`int`
        The internal id of the auction.
    name: :class:`str`
        The name of the character.
    level: :class:`int`
        The level of the character.
    world: :class:`str`
        The world the character is in.
    vocation: :class:`Vocation`
        The vocation of the character.
    sex: :class:`Sex`
        The sex of the character.
    outfit: :class:`OutfitImage`
        The current outfit selected by the user.
    displayed_items: :class:`list` of :class:`DisplayItem`
        The items selected to be displayed.
    sales_arguments: :class:`list` of :class:`SalesArgument`
        The sale arguments selected for the auction.
    auction_start: :class:`datetime.datetime`
        The date when the auction started.
    auction_end: :class:`datetime.datetime`
        The date when the auction ends.
    bid: :class:`int`
        The current bid in Tibia Coins.
    bid_type: :class:`BidType`
        The type of the auction's bid.
    status: :class:`AuctionStatus`
        The current status of the auction.
    hit_points: :class:`int`
        The hit points of the character.
    mana: :class:`int`
        The mana points of the character.
    capacity: :class:`int`
        The character's capacity in ounces.
    speed: :class:`int`
        The character's speed.
    blessings_count: :class:`int`
        The number of blessings the character has.
    outfits_count: :class:`int`
        The number of outfits the character has.
    titles_count: :class:`int`
        The number of titles the character has.
    skills: :class:`list` of :class:`SkillEntry`
        The current skills of the character.
    creation_date: :class:`datetime.datetime`
        The date when the character was created.
    experience: :class:`int`
        The total experience of the character.
    gold: :class:`int`
        The total amount of gold the character has.
    achievement_points: :class:`int`
        The number of achievement points of the character.
    regular_world_transfer_available_date: :class:`datetime.datetmie`
        The date after regular world transfers will be available to purchase and use.
        :obj:`None` indicates it is available immediately.
    charm_expansion: :class:`bool`
        Whether the character has a charm expansion or not.
    available_charm_points: :class:`int`
        The amount of charm points the character has available to spend.
    spent_charm_points: :class:`int`
        The total charm points the character has spent.
    prey_wildcards: :class:`int`
        The number of Prey Wildcards the character has.
    daly_reward_streak: :class:`int`
        The current daily reward streak.
    permanent_hunting_task_slots: :class:`int`
        The number of hunting task slots.
    permanent_prey_slots: :class:`int`
        The number of prey slots.
    hirelings: :class:`int`
        The number of hirelings the character has.
    hireling_jobs: :class:`int`
        The number of hireling jobs the character has.
    hireling_outfits: :class:`int`
        The number of hireling outfits the character has.
    exalted_dust: :class:`int`
        The amount of exalted dust the character has.
    exalted_dust_limit: :class:`int`
        The dust limit of the character.
    boss_points: :class:`int`
        The boss points of the character.
    items: :class:`ItemSummary`
        The items the character has across inventory, depot and item stash.
    store_items: :class:`ItemSummary`
        The store items the character has.
    mounts: :class:`Mounts`
        The mounts the character has unlocked.
    store_mounts: :class:`Mounts`
        The mounts the character has purchased from the store.
    outfits: :class:`Outfits`
        The outfits the character has unlocked.
    store_outfits: :class:`Outfits`
        The outfits the character has purchased from the store.
    familiars: :class:`Familiars`
        The familiars the character has purchased or unlocked.
    blessings: :class:`list` of :class:`BlessingEntry`
        The blessings the character has.
    imbuements: :class:`list` of :class:`str`
        The imbuements the character has unlocked access to.
    charms: :class:`list` of :class:`CharmEntry`
        The charms the character has unlocked.
    completed_cyclopedia_map_areas: :class:`list` of :class:`str`
        The cyclopedia map areas that the character has fully discovered.
    completed_quest_lines: :class:`list` of :class:`str`
        The quest lines the character has fully completed.
    titles: :class:`list` of :class:`str`
        The titles the character has unlocked.
    achievements: :class:`list` of :class:`AchievementEntry`
        The achievements the character has unlocked.
    bestiary_progress: :class:`list` of :class:`BestiaryEntry`
        The bestiary progress of the character.
    bosstiary_progress: :class:`list` of :class:`BosstiaryEntry`
        The bosstiary progress of the character.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hit_points: int = kwargs.get("hit_points", 0)
        self.mana: int = kwargs.get("mana", 0)
        self.capacity: int = kwargs.get("capacity", 0)
        self.speed: int = kwargs.get("speed", 0)
        self.blessings_count: int = kwargs.get("blessings_count", 0)
        self.mounts_count: int = kwargs.get("mounts_count", 0)
        self.outfits_count: int = kwargs.get("outfits_count", 0)
        self.titles_count: int = kwargs.get("titles_count", 0)
        self.skills: List[SkillEntry] = kwargs.get("skills", [])
        self.creation_date: datetime.datetime = kwargs.get("creation_date")
        self.experience: int = kwargs.get("experience", 0)
        self.gold: int = kwargs.get("gold", 0)
        self.achievement_points: int = kwargs.get("achievement_points", 0)
        self.regular_world_transfer_available_date: datetime.datetime = kwargs.get(
            "regular_world_transfer_available_date",
        )
        self.charm_expansion: bool = kwargs.get("charm_expansion", False)
        self.available_charm_points: int = kwargs.get("available_charm_points", 0)
        self.spent_charm_points: int = kwargs.get("spent_charm_points", 0)
        self.daily_reward_streak: int = kwargs.get("daily_reward_streak", 0)
        self.hunting_task_points: int = kwargs.get("hunting_task_points", 0)
        self.prey_wildcards: int = kwargs.get("prey_wildcards", 0)
        self.permanent_hunting_task_slots: int = kwargs.get("permanent_hunting_task_slots", 0)
        self.permanent_prey_slots: int = kwargs.get("permanent_prey_slots", 0)
        self.hirelings: int = kwargs.get("hirelings", 0)
        self.hireling_jobs: int = kwargs.get("hireling_jobs", 0)
        self.hireling_outfits: int = kwargs.get("hireling_outfits", 0)
        self.exalted_dust: int = kwargs.get("exalted_dust", 0)
        self.exalted_dust_limit: int = kwargs.get("exalted_dust_limit", 0)
        self.boss_points: int = kwargs.get("boss_points", 0)
        self.items: ItemSummary = kwargs.get("items")
        self.store_items: ItemSummary = kwargs.get("store_items")
        self.mounts: Mounts = kwargs.get("mounts")
        self.store_mounts: Mounts = kwargs.get("store_mounts")
        self.outfits: Outfits = kwargs.get("outfits")
        self.store_outfits: Outfits = kwargs.get("store_outfits")
        self.blessings: List[BlessingEntry] = kwargs.get("blessings", [])
        self.imbuements: List[str] = kwargs.get("imbuements", [])
        self.charms: List[CharmEntry] = kwargs.get("charms", [])
        self.completed_cyclopedia_map_areas: List[str] = kwargs.get("completed_cyclopedia_map_areas", [])
        self.completed_quest_lines: List[str] = kwargs.get("completed_quest_lines", [])
        self.titles: List[str] = kwargs.get("titles", [])
        self.achievements: List[AchievementEntry] = kwargs.get("achievements", [])
        self.bestiary_progress: List[BestiaryEntry] = kwargs.get("bestiary_progress", [])
        self.bosstiary_progress: List[BestiaryEntry] = kwargs.get("bosstiary_progress", [])

    __slots__ = (
        "hit_points",
        "mana",
        "capacity",
        "speed",
        "blessings_count",
        "mounts_count",
        "outfits_count",
        "titles_count",
        "skills",
        "creation_date",
        "experience",
        "gold",
        "achievement_points",
        "regular_world_transfer_available_date",
        "charm_expansion",
        "available_charm_points",
        "spent_charm_points",
        "daily_reward_streak",
        "hunting_task_points",
        "permanent_hunting_task_slots",
        "permanent_prey_slots",
        "prey_wildcards",
        "hirelings",
        "hireling_jobs",
        "hireling_outfits",
        "exalted_dust",
        "exalted_dust_limit",
        "boss_points",
        "items",
        "store_items",
        "mounts",
        "store_mounts",
        "outfits",
        "store_outfits",
        "familiars",
        "blessings",
        "imbuements",
        "charms",
        "completed_cyclopedia_map_areas",
        "completed_quest_lines",
        "titles",
        "achievements",
        "bestiary_progress",
        "bosstiary_progress",
    )

    # region Properties
    @property
    def completed_bestiary_entries(self):
        """:class:`list` of :class:`BestiaryEntry`: Get a list of completed bestiary entries."""
        return [e for e in self.bestiary_progress if e.completed]

    @property
    def regular_world_transfer_available(self):
        """:class:`bool`: Whether regular world transfers are available immediately for this character."""
        return self.regular_world_transfer_available_date is None
    
    @property
    def skills_map(self) -> Dict[str, 'SkillEntry']:
        """:class:`dict` of :class:`str`, :class:`SkillEntry`: A mapping of skills by their name."""
        return {skill.name: skill for skill in self.skills}
    # endregion

    # region Public Methods
    @classmethod
    def from_content(cls, content, auction_id=0, skip_details=False):
        """Parse an auction detail page from Tibia.com and extracts its data.

        Parameters
        ----------
        content: :class:`str`
            The HTML content of the auction detail page in Tibia.com
        auction_id: :class:`int`, optional
            The ID of the auction.

            It is not possible to extract the ID from the page's content, so it may be passed to assign it manually.
        skip_details: :class:`bool`, optional
            Whether to skip parsing the entire auction and only parse the information shown in lists. False by default.

            This allows fetching basic information like name, level, vocation, world, bid and status, shaving off some
            parsing time.

        Returns
        -------
        :class:`Auction`
            The auction details if found, :obj:`None` otherwise.

        Raises
        ------
        InvalidContent
            If the content does not belong to a auction detail's page.
        """
        parsed_content = parse_tibiacom_content(content, builder='html5lib' if not skip_details else 'lxml')
        auction_row = parsed_content.find("div", attrs={"class": "Auction"})
        if not auction_row:
            if "internal error" in content:
                return None
            raise InvalidContent("content does not belong to a auction details page in Tibia.com")
        auction = cls._parse_auction(auction_row)
        auction.auction_id = auction_id
        if skip_details:
            return auction

        details_tables = cls._parse_tables(parsed_content)
        if "General" in details_tables:
            auction._parse_general_table(details_tables["General"])
        if "ItemSummary" in details_tables:
            auction.items = ItemSummary._parse_table(details_tables["ItemSummary"])
        if "StoreItemSummary" in details_tables:
            auction.store_items = ItemSummary._parse_table(details_tables["StoreItemSummary"])
        if "Mounts" in details_tables:
            auction.mounts = Mounts._parse_table(details_tables["Mounts"])
        if "StoreMounts" in details_tables:
            auction.store_mounts = Mounts._parse_table(details_tables["StoreMounts"])
        if "Outfits" in details_tables:
            auction.outfits = Outfits._parse_table(details_tables["Outfits"])
        if "StoreOutfits" in details_tables:
            auction.store_outfits = Outfits._parse_table(details_tables["StoreOutfits"])
        if "Familiars" in details_tables:
            auction.familiars = Familiars._parse_table(details_tables["Familiars"])
        if "Blessings" in details_tables:
            auction._parse_blessings_table(details_tables["Blessings"])
        if "Imbuements" in details_tables:
            auction.imbuements = cls._parse_single_column_table(details_tables["Imbuements"])
        if "Charms" in details_tables:
            auction._parse_charms_table(details_tables["Charms"])
        if "CompletedCyclopediaMapAreas" in details_tables:
            auction.completed_cyclopedia_map_areas = cls._parse_single_column_table(
                details_tables["CompletedCyclopediaMapAreas"])
        if "CompletedQuestLines" in details_tables:
            auction.completed_quest_lines = cls._parse_single_column_table(details_tables["CompletedQuestLines"])
        if "Titles" in details_tables:
            auction.titles = cls._parse_single_column_table(details_tables["Titles"])
        if "Achievements" in details_tables:
            auction._parse_achievements_table(details_tables["Achievements"])
        if "BestiaryProgress" in details_tables:
            auction._parse_bestiary_table(details_tables["BestiaryProgress"])
        if "BosstiaryProgress" in details_tables:
            auction._parse_bestiary_table(details_tables["BosstiaryProgress"], True)
        return auction
    # endregion

    # region Private Methods
    @classmethod
    def _parse_tables(cls, parsed_content) -> Dict[str, bs4.Tag]:
        """Parse the character details tables.

        Parameters
        ----------
        parsed_content: :class:`bs4.Tag`
            The parsed content of the auction.

        Returns
        -------
        :class:`dict`
            A dictionary of the tables, grouped by their id.
        """
        details_tables = parsed_content.find_all("div", {"class": "CharacterDetailsBlock"})
        return {table["id"]: table for table in details_tables}

    @classmethod
    def _parse_data_table(cls, table) -> Dict[str, str]:
        """Parse a simple data table into a key value mapping.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table to be parsed.

        Returns
        -------
        :class:`dict`
            A mapping containing the table's data.
        """
        rows = table.find_all("tr")
        data = {}
        for row in rows:
            name = row.find("span").text
            value = row.find("div").text
            name = name.lower().strip().replace(" ", "_").replace(":", "")
            data[name] = value
        return data

    def _parse_skills_table(self, table):
        """Parse the skills table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character's skill.
        """
        rows = table.find_all("tr")
        skills = []
        for row in rows:
            cols = row.find_all("td")
            name_c, level_c, progress_c = [c.text for c in cols]
            level = int(level_c)
            progress = float(progress_c.replace("%", ""))
            skills.append(SkillEntry(name=name_c, level=level, progress=progress))
        self.skills = skills

    def _parse_blessings_table(self, table):
        """Parse the blessings table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character's blessings.
        """
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            amount_c, name_c = [c.text for c in cols]
            amount = int(amount_c.replace("x", ""))
            self.blessings.append(BlessingEntry(name_c, amount))

    @classmethod
    def _parse_single_column_table(cls, table):
        """Parse a table with a single column into an array.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            A table with a single column.

        Returns
        -------
        :class:`list` of :class:`str`
            A list with the contents of each row.
        """
        table_content = table.find_all("table", attrs={"class": "TableContent"})[-1]
        _, *rows = table_content.find_all("tr")
        ret = []
        for row in rows:
            col = row.find("td")
            text = col.text
            if "more entries" in text:
                continue
            ret.append(text)
        return ret

    def _parse_charms_table(self, table):
        """Parse the charms table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the charms.
        """
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) != 2:
                continue
            cost_c, name_c = [c.text for c in cols]
            cost = parse_integer(cost_c.replace("x", ""))
            self.charms.append(CharmEntry(name_c, cost))

    def _parse_achievements_table(self, table):
        """Parse the achievements table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the achievements.
        """
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            col = row.find("td")
            text = col.text.strip()
            if "more entries" in text:
                continue
            secret = col.find("img") is not None
            self.achievements.append(AchievementEntry(text, secret))

    def _parse_bestiary_table(self, table, bosstiary=False):
        """Parse the bestiary table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the bestiary information.
        """
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) != 3:
                continue
            step_c, kills_c, name_c = [c.text for c in cols]
            kills = parse_integer(kills_c.replace("x", ""))
            step = int(step_c)
            if not bosstiary:
                self.bestiary_progress.append(BestiaryEntry(name_c, kills, step))
            else:
                self.bosstiary_progress.append(BestiaryEntry(name_c, kills, step))

    @classmethod
    def _parse_page_items(cls, content, entry_class):
        """Parse the elements of a page in the items, mounts and outfits.

        Attributes
        ----------
        content: :class:`str`
            The HTML content in the page.
        entry_class:
            The class defining the elements.

        Returns
        -------
            The entries contained in the page.
        """
        parsed_content = parse_tibiacom_content(content, builder='html5lib')
        item_boxes = parsed_content.find_all("div", attrs={"class": "CVIcon"})
        entries = []
        for item_box in item_boxes:
            item = entry_class._parse_image_box(item_box)
            if item:
                entries.append(item)
        return entries

    def _parse_general_table(self, table):
        """Parse the general information table and assigns its values.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table with general information.
        """
        content_containers = table.find_all("table", {"class": "TableContent"})
        general_stats = self._parse_data_table(content_containers[0])
        self.hit_points = parse_integer(general_stats.get("hit_points", "0"))
        self.mana = parse_integer(general_stats.get("mana", "0"))
        self.capacity = parse_integer(general_stats.get("capacity", "0"))
        self.speed = parse_integer(general_stats.get("speed", "0"))
        self.mounts_count = parse_integer(general_stats.get("mounts", "0"))
        self.outfits_count = parse_integer(general_stats.get("outfits", "0"))
        self.titles_count = parse_integer(general_stats.get("titles", "0"))
        self.blessings_count = parse_integer(re.sub(r"/d+", "", general_stats.get("blessings", "0")))

        self._parse_skills_table(content_containers[1])

        additional_stats = self._parse_data_table(content_containers[2])
        self.creation_date = parse_tibia_datetime(additional_stats.get("creation_date", "").replace("\xa0", " "))
        self.experience = parse_integer(additional_stats.get("experience", "0"))
        self.gold = parse_integer(additional_stats.get("gold", "0"))
        self.achievement_points = parse_integer(additional_stats.get("achievement_points", "0"))

        transfer_data = self._parse_data_table(content_containers[3])
        transfer_text = transfer_data.get("regular_world_transfer")
        if "after" in transfer_text:
            date_string = transfer_text.split("after ")[1]
            self.regular_world_transfer_available_date = parse_tibia_datetime(date_string)

        charms_data = self._parse_data_table(content_containers[4])
        self.charm_expansion = "yes" in charms_data.get("charm_expansion", "")
        self.available_charm_points = parse_integer(charms_data.get("available_charm_points"))
        self.spent_charm_points = parse_integer(charms_data.get("spent_charm_points"))

        daily_rewards_data = self._parse_data_table(content_containers[5])
        self.daily_reward_streak = parse_integer(daily_rewards_data.popitem()[1])

        hunting_data = self._parse_data_table(content_containers[6])
        self.hunting_task_points = parse_integer(hunting_data.get("hunting_task_points", ""))
        self.permanent_hunting_task_slots = parse_integer(hunting_data.get("permanent_hunting_task_slots", ""))
        self.permanent_prey_slots = parse_integer(hunting_data.get("permanent_prey_slots", ""))
        self.prey_wildcards = parse_integer(hunting_data.get("prey_wildcards", ""))

        hirelings_data = self._parse_data_table(content_containers[7])
        self.hirelings = parse_integer(hirelings_data.get("hirelings", ""))
        self.hireling_jobs = parse_integer(hirelings_data.get("hireling_jobs", ""))
        self.hireling_outfits = parse_integer(hirelings_data.get("hireling_outfits", ""))
        if len(content_containers) >= 9:
            dust_data = self._parse_data_table(content_containers[8])
            dust_values = dust_data.get("exalted_dust", "0/0").split("/")
            self.exalted_dust = parse_integer(dust_values[0])
            self.exalted_dust_limit = parse_integer(dust_values[1])
        if len(content_containers) >= 10:
            boss_data = self._parse_data_table(content_containers[9])
            self.boss_points = parse_integer(boss_data.get("boss_points", ""))
    # endregion


class OutfitImage(abc.Serializable):
    """The image of the outfit currently being worn by the character.

    Attributes
    ----------
    image_url: :class:`str`
        The URL of the image.
    outfit_id: :class:`int`
        The ID of the outfit.
    addons: :class:`int`
        The addons displayed in the outfit.
    """

    def __init__(self, **kwargs):
        self.image_url: str = kwargs.get("image_url")
        self.outfit_id: int = kwargs.get("outfit_id", 0)
        self.addons: int = kwargs.get("addons", 0)

    __slots__ = (
        "image_url",
        "outfit_id",
        "addons",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} outfit_id={self.outfit_id} addons={self.addons} " \
               f"image_url={self.image_url!r}>"


class PaginatedSummary(abc.Serializable):
    """Represents a paginated summary in the character auction section.

    Attributes
    ----------
    page: :class:`int`
        The current page being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results: :class:`int`
        The total number of results.
    entries: :class:`list`
        The entries.
    fully_fetched: :class:`bool`
        Whether the summary was fetched completely, including all other pages.
    """

    entry_class = None

    def __init__(self, **kwargs):
        self.page: int = kwargs.get("page", 1)
        self.total_pages: int = kwargs.get("total_pages", 1)
        self.results: int = kwargs.get("results", 0)
        self.fully_fetched: bool = kwargs.get("fully_fetched", False)
        self.entries: List[DisplayImage] = kwargs.get("entries", [])

    __slots__ = (
        "page",
        "total_pages",
        "results",
        "fully_fetched",
        "entries",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} page={self.page} total_pages={self.total_pages} results={self.results} " \
               f"fully_fetched={self.fully_fetched} len(entries)={len(self.entries)}>"

    # region Public Methods
    def get_by_name(self, name):
        """Get an entry by its name.

        Parameters
        ----------
        name: :class:`str`
            The name of the entry, case insensitive.

        Returns
        -------
        :class:`object`:
            The entry matching the name.
        """
        return next((e for e in self.entries if e.name.lower() == name.lower()), None)

    def search(self, value):
        """Search an entry by its name.

        Parameters
        ----------
        value: :class:`str`
            The value to look for.

        Returns
        -------
        :class:`list`
            A list of entries with names containing the search term.
        """
        return [e for e in self.entries if value.lower() in e.name.lower()]

    def get_by_id(self, name):
        """Get an entry by its id.

        Parameters
        ----------
        name: :class:`str`
            The name of the entry, case insensitive.

        Returns
        -------
        :class:`object`:
            The entry matching the name.
        """
        return NotImplemented
    # endregion

    # region Private Methods
    def _parse_pagination(self, parsed_content):
        pagination_block = parsed_content.find("div", attrs={"class": "BlockPageNavigationRow"})
        if pagination_block is not None:
            self.page, self.total_pages, self.results = parse_pagination(pagination_block)
    # endregion


class ItemSummary(PaginatedSummary):
    """Items in a character's inventory and depot.

    Attributes
    ----------
    page: :class:`int`
        The current page being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results: :class:`int`
        The total number of results.
    entries: :class:`list` of :class:`DisplayItem`
        The character's items.
    fully_fetched: :class:`bool`
        Whether the summary was fetched completely, including all other pages.
    """

    entries: List[DisplayItem]
    entry_class = DisplayItem

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_by_id(self, entry_id):
        """Get an item by its item id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the item.

        Returns
        -------
        :class:`DisplayItem`
            The item matching the id.
        """
        return next((e for e in self.entries if e.item_id == entry_id), None)

    @classmethod
    def _parse_table(cls, table):
        """Parse the item summary table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the item summary.

        Returns
        -------
        :class:`ItemSummary`
            The item summary contained in the table.
        """
        summary = cls()
        summary._parse_pagination(table)
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayItem._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class Mounts(PaginatedSummary):
    """The mounts a character has unlocked or purchased.

    Attributes
    ----------
    page: :class:`int`
        The current page being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results: :class:`int`
        The total number of results.
    entries: :class:`list` of :class:`DisplayMount`
        The character's mounts.
    fully_fetched: :class:`bool`
        Whether the summary was fetched completely, including all other pages.
    """

    entries: List[DisplayMount]
    entry_class = DisplayMount

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_by_id(self, entry_id):
        """Get a mount by its mount id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the mount.

        Returns
        -------
        :class:`DisplayMount`
            The mount matching the id.
        """
        return next((e for e in self.entries if e.mount_id == entry_id), None)

    @classmethod
    def _parse_table(cls, table):
        summary = cls()
        summary._parse_pagination(table)
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayMount._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class Familiars(PaginatedSummary):
    """The familiars the character has unlocked or purchased.

    Attributes
    ----------
    page: :class:`int`
        The current page being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results: :class:`int`
        The total number of results.
    entries: :class:`list` of :class:`DisplayFamiliar`
        The familiars the character has unlocked or purchased.
    fully_fetched: :class:`bool`
        Whether the summary was fetched completely, including all other pages.
    """

    entries: List[DisplayFamiliar]
    entry_class = DisplayFamiliar

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_by_id(self, entry_id):
        """Get an outfit by its familiar id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the outfit.

        Returns
        -------
        :class:`DisplayOutfit`
            The outfit matching the id.
        """
        return next((e for e in self.entries if e.familiar_id == entry_id), None)

    @classmethod
    def _parse_table(cls, table):
        """Parse the outfits table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character outfits.

        Returns
        -------
        :class:`Outfits`
            The outfits contained in the table.
        """
        summary = cls()
        summary._parse_pagination(table)
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayFamiliar._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class Outfits(PaginatedSummary):
    """The outfits the character has unlocked or purchased.

    Attributes
    ----------
    page: :class:`int`
        The current page being displayed.
    total_pages: :class:`int`
        The total number of pages.
    results: :class:`int`
        The total number of results.
    entries: :class:`list` of :class:`DisplayOutfit`
        The outfits the character has unlocked or purchased.
    fully_fetched: :class:`bool`
        Whether the summary was fetched completely, including all other pages.
    """

    entries: List[DisplayOutfit]
    entry_class = DisplayOutfit

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_by_id(self, entry_id):
        """Get an outfit by its outfit id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the outfit.

        Returns
        -------
        :class:`DisplayOutfit`
            The outfit matching the id.
        """
        return next((e for e in self.entries if e.outfit_id == entry_id), None)

    @classmethod
    def _parse_table(cls, table):
        """Parse the outfits table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character outfits.

        Returns
        -------
        :class:`Outfits`
            The outfits contained in the table.
        """
        summary = cls()
        summary._parse_pagination(table)
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayOutfit._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class SalesArgument(abc.Serializable):
    """Represents a sales argument.

    Sales arguments can be selected when creating an auction, and allow the user to highlight certain
    character features in the auction listing.

    Attributes
    ----------
    category_image: :class:`str`
        The URL to the category icon.
    content: :class:`str`
        The content of the sales argument.
    """

    __slots__ = (
        "category_id",
        "category_image",
        "content",
    )

    def __init__(self, **kwargs):
        self.category_id: int = kwargs.get("category_id", 0)
        self.category_image: str = kwargs.get("category_image")
        self.content: str = kwargs.get("content")

    def __repr__(self):
        return f"<{self.__class__.__name__} category_id={self.category_id} content={self.content!r} " \
               f"category_image={self.category_image}>"


class SkillEntry(abc.Serializable):
    """Represents the character's skills.

    Attributes
    ----------
    name: :class:`name`
        The name of the skill.
    level: :class:`int`
        The current level.
    progress: :class:`float`
        The percentage of progress for the next level.
    """

    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name")
        self.level: int = kwargs.get("level", 0)
        self.progress: float = kwargs.get("progress", 0.0)

    __slots__ = (
        "name",
        "level",
        "progress",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name!r} level={self.level} progress={self.progress}>"
