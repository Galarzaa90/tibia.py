import datetime
import re
import urllib.parse

from typing import List

from tibiapy import abc, Sex, Vocation
from tibiapy.abc import BaseCharacter
from tibiapy.enums import BidType
from tibiapy.utils import convert_line_breaks, get_tibia_url, parse_integer, parse_tibia_datetime, parse_tibia_money, \
    parse_tibiacom_content, \
    try_enum

__all__ = (
    "CharacterBazaar",
    "DisplayItem",
    "ListedAuction",
    "AuctionDetails",
    "SalesArgument",
    "SkillEntry",
)

results_pattern = re.compile(r'Results: (\d+)')
char_info_regex = re.compile(r'Level: (\d+) \| Vocation: ([\w\s]+)\| (\w+) \| World: (\w+)')
id_addon_regex = re.compile(r'(\d+)_(\d)\.gif')
id_regex = re.compile(r'(\d+).gif')
description_regex = re.compile(r'"(?:an?\s)?([^"]+)"')
quotes = re.compile(r'"([^"]+)"')


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
    entries: :class:`list` of :class:`ListedAuction`
        The auctions displayed."""
    def __init__(self, **kwargs):
        self.page = kwargs.get("page", 1)
        self.total_pages = kwargs.get("total_pages", 1)
        self.results_count = kwargs.get("results_count", 0)
        self.entries = kwargs.get("entries", [])

    __slots__ = (
        "page",
        "total_pages",
        "results_count",
        "entries",
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} page={self.page} total_pages={self.total_pages}" \
               f"results_count={self.results_count}>"

    @classmethod
    def get_current_auctions_url(cls):
        """Gets the URL to the list of current auctions in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the current auctions section in Tibia.com
        """
        return get_tibia_url("charactertrade", "currentcharactertrades")

    @classmethod
    def get_auctions_history_url(cls):
        """Gets the URL to the auction history in Tibia.com

        Returns
        -------
        :class:`str`
            The URL to the auction history section in Tibia.com
        """
        return get_tibia_url("charactertrade", "pastcharactertrades")

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content, builder='html5lib')
        tables = parsed_content.find_all("div", attrs={"class": "TableContainer"})
        filter_table = None
        if len(tables) == 1:
            auctions_table = tables[0]
        else:
            filter_table, auctions_table, *_ = tables

        bazaar = cls()

        page_navigation_row = parsed_content.find("td", attrs={"class": "PageNavigation"})
        pages_div, results_div = page_navigation_row.find_all("div")
        page_links = pages_div.find_all("a")
        listed_pages = [int(p.text) for p in page_links]
        if listed_pages:
            bazaar.page = next((x for x in range(1, listed_pages[-1] + 1) if x not in listed_pages), 0)
            bazaar.total_pages = max(int(page_links[-1].text), bazaar.page)
        bazaar.results_count = int(results_pattern.search(results_div.text).group(1))

        auction_rows = auctions_table.find_all("div", attrs={"class": "Auction"})
        for auction_row in auction_rows:
            auction = ListedAuction._parse_auction(auction_row)

            bazaar.entries.append(auction)
        return bazaar


class DisplayItem(abc.Serializable):
    """Represents an item displayed on an auction, or the character's items in the auction detail.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the item's image.
    name: :class:`str`
        The item's name.
    count: :class:`int`
        The item's count.
    item_id: :class:`int`
        The item's client id.
    """
    def __init__(self, **kwargs):
        self.image_url: str = kwargs.get("image_url")
        self.name: str = kwargs.get("name")
        self.count: int = kwargs.get("count", 1)
        self.item_id: int = kwargs.get("item_id", 0)

    __slots__ = (
        "image_url",
        "name",
        "count",
        "item_id",
    )

    @classmethod
    def _parse_item_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.find("img")
        if not img_tag:
            return None
        amount_text = item_box.find("div", attrs={"class": "ObjectAmount"})
        amount = parse_tibia_money(amount_text.text) if amount_text else 1
        item_id = 0
        name = None
        m = id_regex.search(img_tag["src"])
        if m:
            item_id = int(m.group(1))
        m = description_regex.search(description)
        if m:
            name = m.group(1)
        return DisplayItem(image_url=img_tag["src"], name=name, count=amount, item_id=item_id)


class DisplayItem(abc.Serializable):
    """Represents an item displayed on an auction, or the character's items in the auction detail.

    Attributes
    ----------
    image_url: :class:`str`
        The URL to the item's image.
    name: :class:`str`
        The item's name.
    count: :class:`int`
        The item's count.
    item_id: :class:`int`
        The item's client id.
    """
    def __init__(self, **kwargs):
        self.image_url: str = kwargs.get("image_url")
        self.name: str = kwargs.get("name")
        self.count: int = kwargs.get("count", 1)
        self.item_id: int = kwargs.get("item_id", 0)

    __slots__ = (
        "image_url",
        "name",
        "count",
        "item_id",
    )

    @classmethod
    def _parse_item_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.find("img")
        if not img_tag:
            return None
        amount_text = item_box.find("div", attrs={"class": "ObjectAmount"})
        amount = parse_tibia_money(amount_text.text) if amount_text else 1
        item_id = 0
        name = None
        m = id_regex.search(img_tag["src"])
        if m:
            item_id = int(m.group(1))
        m = description_regex.search(description)
        if m:
            name = m.group(1)
        return DisplayItem(image_url=img_tag["src"], name=name, count=amount, item_id=item_id)


class DisplayImage(abc.Serializable):
    """Represents an item displayed on an auction, or the character's items in the auction detail.

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

    @classmethod
    def _parse_image_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.find("img")
        if not img_tag:
            return None
        m = quotes.search(description)
        if m:
            description = m.group(1)
        return cls(image_url=img_tag["src"], name=description)


class DisplayMount(DisplayImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        mount_id = kwargs.get("mount_id", 0)

    __slots__ = (
        "mount_id"
    )

    @classmethod
    def _parse_image_box(cls, item_box):
        mount = super()._parse_image_box(item_box)
        m = id_regex.search(mount.image_url)
        if m:
            mount.mount_id = int(m.group(1))
        return mount


class DisplayOutfit(DisplayImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        outfit_id = kwargs.get("outfit_id", 0)
        addons = kwargs.get("addons", 0)

    __slots__ = (
        "outfit_id"
        "addons"
    )

    @classmethod
    def _parse_image_box(cls, item_box):
        outfit = super()._parse_image_box(item_box)
        m = id_addon_regex.search(outfit.image_url)
        if m:
            outfit.outfit_id = int(m.group(1))
            outfit.addons = int(m.group(2))
        return outfit


class ListedAuction(BaseCharacter, abc.Serializable):
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
    status: :class:`str`
        The current status of the auction.
    """
    def __init__(self, **kwargs):
        self.auction_id: int = kwargs.get("auction_id", 0)
        self.name: str = kwargs.get("name")
        self.level: int = kwargs.get("level", 0)
        self.world: str = kwargs.get("world")
        self.vocation: Vocation = kwargs.get("vocation")
        self.sex: Sex = kwargs.get("sex")
        self.outfit: str = kwargs.get("outfit")
        self.displayed_items: List[DisplayItem] = kwargs.get("displayed_items", [])
        self.sales_arguments: List[SalesArgument] = kwargs.get("sales_arguments", [])
        self.auction_start: datetime.datetime = kwargs.get("auction_start")
        self.auction_end: datetime.datetime = kwargs.get("auction_end")
        self.bid: int = kwargs.get("bid", 0)
        self.bid_type: BidType = kwargs.get("bid_type")
        self.status: str = kwargs.get("status")

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

    @property
    def character_url(self):
        """
        :class:`str`: The URL of the character's information page on Tibia.com
        """
        return BaseCharacter.get_url(self.name)

    @property
    def url(self):
        """
        :class:`str`: The URL to this auction's detail page on Tibia.com
        """
        return self.get_url(self.auction_id)

    @classmethod
    def get_url(cls, auction_id):
        """Gets the URL to the Tibia.com detail page of an auction with a given id.

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

    @classmethod
    def _parse_auction(cls, auction_row, auction_id=0):
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
            item = DisplayItem._parse_item_box(item_box)
            if item:
                auction.displayed_items.append(item)
        dates_containers = auction_row.find("div", {"class": "ShortAuctionData"})
        start_date_tag, end_date_tag, *_ = dates_containers.find_all("div", {"class": "ShortAuctionDataValue"})
        auction.auction_start = parse_tibia_datetime(start_date_tag.text.replace('\xa0', ' '))
        auction.auction_end = parse_tibia_datetime(end_date_tag.text.replace('\xa0', ' '))
        bids_container = auction_row.find("div", {"class": "ShortAuctionDataBidRow"})
        bid_tag = bids_container.find("div", {"class", "ShortAuctionDataValue"})
        bid_type_tag = bids_container.find_all("div", {"class", "ShortAuctionDataLabel"})[-1]
        bid_type_str = bid_type_tag.text.replace(":", "").strip()
        auction.bid_type = try_enum(BidType, bid_type_str)
        auction.bid = parse_integer(bid_tag.text)
        status = "in progress"
        auction_body_block = auction_row.find("div", {"class", "CurrentBid"})
        auction_info_tag = auction_body_block.find("div", {"class": "AuctionInfo"})
        if auction_info_tag:
            convert_line_breaks(auction_info_tag)
            status = auction_info_tag.text.replace("\n", " ").replace("  ", " ")
        auction.status = status
        argument_entries = auction_row.find_all("div", {"class": "Entry"})
        for entry in argument_entries:
            img = entry.find("img")
            auction.sales_arguments.append(SalesArgument(content=entry.text, category_image=img["src"]))
        return auction


class AuctionDetails(ListedAuction):
    """Represents the details of an auction.

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
    status: :class:`str`
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
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hit_points = kwargs.get("hit_points")
        self.mana = kwargs.get("mana")
        self.capacity = kwargs.get("capacity")
        self.speed = kwargs.get("speed")
        self.blessings_count = kwargs.get("blessings_count")
        self.mounts_count = kwargs.get("mounts_count")
        self.outfits_count = kwargs.get("outfits_count")
        self.titles_count = kwargs.get("titles_count")
        self.skills = kwargs.get("skills")
        self.creation_date = kwargs.get("creation_date")
        self.experience = kwargs.get("experience")
        self.gold = kwargs.get("gold")
        self.achievement_points = kwargs.get("achievement_points")
        self.regular_world_transfer_available = kwargs.get("regular_world_transfer_available")
        self.charm_expansion = kwargs.get("charm_expansion")
        self.available_charm_points = kwargs.get("available_charm_points")
        self.spent_charm_points = kwargs.get("spent_charm_points")
        self.daily_reward_streak = kwargs.get("daily_reward_streak")
        self.hunting_task_points = kwargs.get("hunting_task_points")
        self.permanent_hunting_task_slots = kwargs.get("permanent_hunting_task_slots")
        self.permanent_prey_slots = kwargs.get("permanent_prey_slots")
        self.hirelings = kwargs.get("hirelings")
        self.hireling_jobs = kwargs.get("hireling_jobs")
        self.hireling_outfits = kwargs.get("hireling_outfits")
        self.items = kwargs.get("items")
        self.store_items = kwargs.get("store_items")
        self.mounts = kwargs.get("mounts")
        self.store_mounts = kwargs.get("store_mounts")
        self.outfits = kwargs.get("outfits")
        self.store_outfits = kwargs.get("store_outfits")
        self.blessings = kwargs.get("blessings", [])
        self.imbuements = kwargs.get("imbuements", [])
        self.charms = kwargs.get("charms", [])
        self.completed_cyclopedia_map_areas = kwargs.get("completed_cyclopedia_map_areas", [])
        self.completed_quest_lines = kwargs.get("completed_quest_lines", [])
        self.titles = kwargs.get("titles", [])
        self.achievements = kwargs.get("achievements", [])
        self.bestiary_progress = kwargs.get("bestiary_progress", [])

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
        "regular_world_transfer_available",
        "charm_expansion",
        "available_charm_points",
        "spent_charm_points",
        "daily_reward_streak",
        "hunting_task_points",
        "permanent_hunting_task_slots",
        "permanent_prey_slots",
        "hirelings",
        "hireling_jobs",
        "hireling_outfits",
        "items",
        "store_items",
        "mounts",
        "store_mounts",
        "outfits",
        "store_outfits",
        "blessings",
        "imbuements",
        "charms",
        "completed_cyclopedia_map_areas",
        "completed_quest_lines",
        "titles",
        "achievements",
        "bestiary_progress",
    )

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content, builder='html5lib')
        auction_row = parsed_content.find("div", attrs={"class": "Auction"})
        auction = cls._parse_auction(auction_row)

        details_tables = cls._parse_tables(parsed_content)
        if "General" in details_tables:
            auction._parse_general_table(details_tables["General"])
        if "ItemSummary" in details_tables:
            auction._parse_items_table(details_tables["ItemSummary"])
        if "StoreItemSummary" in details_tables:
            auction._parse_store_items_table(details_tables["StoreItemSummary"])
        if "Mounts" in details_tables:
            auction._parse_mounts_table(details_tables["Mounts"])
        if "StoreMounts" in details_tables:
            auction._parse_store_mounts_table(details_tables["StoreMounts"])
        if "Outfits" in details_tables:
            auction._parse_outfits_table(details_tables["Outfits"])
        if "StoreOutfits" in details_tables:
            auction._parse_store_outfits_table(details_tables["StoreOutfits"])
        if "Blessings" in details_tables:
            auction._parse_blessings_table(details_tables["Blessings"])
        if "Imbuements" in details_tables:
            auction.imbuements = cls._parse_single_row_table(details_tables["Imbuements"])
        if "Charms" in details_tables:
            auction._parse_charms_table(details_tables["Charms"])
        if "CompletedCyclopediaMapAreas" in details_tables:
            auction.completed_cyclopedia_map_areas = cls._parse_single_row_table(
                details_tables["CompletedCyclopediaMapAreas"])
        if "CompletedQuestLines" in details_tables:
            auction.completed_quest_lines = cls._parse_single_row_table(details_tables["CompletedQuestLines"])
        if "Titles" in details_tables:
            auction.titles = cls._parse_single_row_table(details_tables["Titles"])
        if "Achievements" in details_tables:
            auction._parse_achievements_table(details_tables["Achievements"])
        if "BestiaryProgress" in details_tables:
            auction._parse_bestiary_table(details_tables["BestiaryProgress"])
        return auction

    @classmethod
    def _parse_tables(cls, parsed_content):
        details_tables = parsed_content.find_all("div", {"class": "CharacterDetailsBlock"})
        return {table["id"]: table for table in details_tables}

    def _parse_data_table(self, table):
        rows = table.find_all("tr")
        data = {}
        for row in rows:
            name = row.find("span").text
            value = row.find("div").text
            name = name.lower().strip().replace(" ", "_").replace(":", "")
            data[name] = value
        return data

    def parse_skills_table(self, table):
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
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            amount_c, name_c = [c.text for c in cols]
            amount = int(amount_c.replace("x", ""))
            self.blessings.append(BlessingEntry(name_c, amount))

    @classmethod
    def _parse_single_row_table(cls, table):
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
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cost_c, name_c = [c.text for c in cols]
            cost = int(cost_c.replace("x", ""))
            self.charms.append(CharmEntry(name_c, cost))

    def _parse_achievements_table(self, table):
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            col = row.find("td")
            text = col.text.strip()
            if "more entries" in text:
                continue
            secret = col.find("img") is not None
            self.achievements.append(AchievementEntry(text, secret))

    def _parse_bestiary_table(self, table):
        table_content = table.find("table", attrs={"class": "TableContent"})
        _, *rows = table_content.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if "more entries" in row.text:
                continue
            step_c, kills_c, name_c = [c.text for c in cols]
            kills = parse_integer(kills_c.replace("x", ""))
            step = int(step_c)
            self.bestiary_progress.append(BestiaryEntry(name_c, kills, step))

    def _parse_items_table(self, table):
        self.items = ItemSummary()
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayItem._parse_item_box(item_box)
            if item:
                self.items.entries.append(item)

    def _parse_store_items_table(self, table):
        self.store_items = StoreSummary()
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for item_box in item_boxes:
            item = DisplayItem._parse_item_box(item_box)
            if item:
                self.store_items.entries.append(item)

    def _parse_mounts_table(self, table):
        self.mounts = Mounts()
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for image_box in item_boxes:
            mount = DisplayMount._parse_image_box(image_box)
            if mount:
                self.mounts.entries.append(mount)

    def _parse_store_mounts_table(self, table):
        self.store_mounts = Mounts()
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for image_box in item_boxes:
            mount = DisplayMount._parse_image_box(image_box)
            if mount:
                self.store_mounts.entries.append(mount)

    def _parse_outfits_table(cls, table):
        entries = []
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for image_box in item_boxes:
            outfit = DisplayOutfit._parse_image_box(image_box)
            if outfit:
                entries.append(outfit)
        return entries

    def _parse_store_outfits_table(self, table):
        self.store_outfits = Outfits()
        item_boxes = table.find_all("div", attrs={"class": "CVIcon"})
        for image_box in item_boxes:
            outfit = DisplayOutfit._parse_image_box(image_box)
            if outfit:
                self.store_outfits.entries.append(outfit)

    def _parse_general_table(self, table):
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

        self.parse_skills_table(content_containers[1])

        additional_stats = self._parse_data_table(content_containers[2])
        self.creation_date = parse_tibia_datetime(additional_stats.get("creation_date", "").replace("\xa0", " "))
        self.experience = parse_integer(additional_stats.get("experience", "0"))
        self.gold = parse_integer(additional_stats.get("gold", "0"))
        self.achievement_points = parse_integer(additional_stats.get("achievement_points", "0"))

        charms_data = self._parse_data_table(content_containers[4])
        self.charm_expansion = "yes" in charms_data.get("charms_expansion", "")
        self.available_charm_points = parse_integer(charms_data.get("available_charm_points"))
        self.spent_charm_points = parse_integer(charms_data.get("spent_charm_points"))

        daily_rewards_data = self._parse_data_table(content_containers[5])
        self.daily_reward_streak = parse_integer(daily_rewards_data.popitem()[1])

        hunting_data = self._parse_data_table(content_containers[6])
        self.hunting_task_points = parse_integer(hunting_data.get("hunting_task_points", ""))
        self.permanent_hunting_task_slots = parse_integer(hunting_data.get("permanent_hunting_task_slots", ""))
        self.permanent_prey_slots = parse_integer(hunting_data.get("permanent_prey_slots", ""))

        hirelings_data = self._parse_data_table(content_containers[7])
        self.hirelings = parse_integer(hirelings_data.get("hirelings", ""))
        self.hireling_jobs = parse_integer(hirelings_data.get("hireling_jobs", ""))
        self.hireling_outfits = parse_integer(hirelings_data.get("hireling_outfits", ""))


class SalesArgument(abc.Serializable):
    """Represents a sales argument.

    Sales arguments can be selected when creating an auction, and allow the user to highlight certain
    character features in the auction listing.

    Attributes
    ----------
    category_image: :class:`str`
        The URL to the category icon.
    content: :class:`str`
        The content of the sales argument."""
    def __init__(self, **kwargs):
        self.category_image = kwargs.get("category_image")
        self.content = kwargs.get("content")

    __slots__ = (
        "category_image",
        "content",
    )


class SkillEntry(abc.Serializable):
    """Represents the character's skills.

    Attributes
    ----------
    name: :class:`name`
        The name of the skill.
    level: :class:`int`
        The current level.
    progress: :class:`float`
        The percentage of progress for the next level."""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.level = kwargs.get("level")
        self.progress = kwargs.get("progress")

    __slots__ = (
        "name",
        "level",
        "progress",
    )


class OutfitImage(abc.Serializable):
    def __init__(self, **kwargs):
        self.image_url = kwargs.get("image_url")
        self.outfit_id = kwargs.get("outfit_id")
        self.addons = kwargs.get("addons")

    __slots__ = (
        "image_url",
        "outfit_id",
        "addons",
    )


class PaginatedSummary(abc.Serializable):
    def __init__(self, **kwargs):
        self.page = kwargs.get("page", 1)
        self.total_pages = kwargs.get("total_pages", 1)
        self.results = kwargs.get("results", 0)
        self.entries = kwargs.get("entries", [])

    __slots__ = (
        "page",
        "total_pages",
        "results",
        "entries",
    )

class ItemSummary(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StoreSummary(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Mounts(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StoreMounts(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Outfits(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class StoreOutfits(PaginatedSummary):
    entries: List[DisplayItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BlessingEntry(abc.Serializable):

    def __init__(self, name, amount=0):
        self.name: str = name
        self.amount: int = amount

    __slots__ = (
        "name",
        "amount",
    )


class CharmEntry(abc.Serializable):

    def __init__(self, name, cost=0):
        self.name: str = name
        self.cost: int = cost

    __slots__ = (
        "name",
        "cost",
    )


class AchievementEntry(abc.Serializable):
    def __init__(self, name, secret=False):
        self.name: str = name
        self.secret: int = secret

    __slots__ = (
        "name",
        "secret",
    )


class BestiaryEntry(abc.Serializable):
    def __init__(self, name, kills, step):
        self.name: str = name
        self.kills: int = kills
        self.step: int = step

    __slots__ = (
        "name",
        "kills",
        "step",
    )