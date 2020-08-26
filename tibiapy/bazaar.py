import urllib.parse
import re

from tibiapy import abc, Sex, Vocation
from tibiapy.abc import BaseCharacter
from tibiapy.utils import get_tibia_url, parse_integer, parse_tibia_datetime, parse_tibiacom_content, try_enum

__all__ = (
    "CurrentAuctions",
    "DisplayItem",
    "ListedAuction",
    "AuctionDetails",
    "SalesArgument"
)

char_info_regex = re.compile(r'Level: (\d+) \| Vocation: ([\w\s]+)\| (\w+) \| World: (\w+)')


class CurrentAuctions(abc.Serializable):
    def __init__(self, **kwargs):
        self.entries = kwargs.get("entries")

    __slots__ = (
        "page",
        "total_pages",
        "results_coount",
        "entries",
    )

    @classmethod
    def get_url(cls):
        return get_tibia_url("charactertrade", "currentcharactertrades")

    @classmethod
    def from_content(cls, content):
        parsed_content = parse_tibiacom_content(content, builder='html5lib')
        tables = parsed_content.find_all("div", attrs={"class": "TableContainer"})
        filter_table, auctions_table = tables

        auction_rows = auctions_table.find_all("div", attrs={"class": "Auction"})
        entries = []
        for auction_row in auction_rows:
            header_container = auction_row.find("div", attrs={"class": "AuctionHeader"})
            char_name_container = header_container.find("div", attrs={"class": "AuctionCharacterName"})
            char_link = char_name_container.find("a")
            url = urllib.parse.urlparse(char_link["href"])
            query = urllib.parse.parse_qs(url.query)
            auction_id = int(query["auctionid"][0])
            name = char_link.text
            auction = ListedAuction(name=name, auction_id=auction_id)
            char_name_container.replaceWith('')
            m = char_info_regex.search(header_container.text)
            if m:
                auction.level = int(m.group(1))
                auction.vocation = try_enum(Vocation, m.group(2).strip())
                auction.sex = try_enum(Sex, m.group(3).strip().lower())
                auction.world = m.group(4)
            outfit_img = auction_row.find("img", {"class": "AuctionOutfitImage"})
            auction.outfit = outfit_img["src"]

            item_boxes = auction_row.find_all("div", attrs={"class": "CVIcon"})
            for item_box in item_boxes:
                description = item_box["title"]
                img_tag = item_box.find("img")
                if not img_tag:
                    continue
                amount_text = item_box.find("div", attrs={"class": "ObjectAmount"})
                amount = int(amount_text.text) if amount_text else 1
                auction.items.append(DisplayItem(image_url=img_tag["src"], description=description, count=amount))

            dates_containers = auction_row.find("div", {"class": "ShortAuctionData"})
            start_date_tag, end_date_tag, *_ = dates_containers.find_all("div", {"class": "ShortAuctionDataValue"})
            auction.auction_start = parse_tibia_datetime(start_date_tag.text.replace('\xa0', ' '))
            auction.auction_end = parse_tibia_datetime(end_date_tag.text.replace('\xa0', ' '))

            bids_container = auction_row.find("div", {"class": "ShortAuctionDataBidRow"})
            current_bid_tag = bids_container.find("div", {"class", "ShortAuctionDataValue"})
            auction.current_bid = parse_integer(current_bid_tag.text)

            argument_entries = auction_row.find_all("div", {"class": "Entry"})
            for entry in argument_entries:
                img = entry.find("img")
                auction.sales_arguments.append(SalesArgument(content=entry.text, category_image=img["src"]))

            entries.append(auction)
        return cls(entries=entries)


class DisplayItem(abc.Serializable):
    def __init__(self, **kwargs):
        self.image_url = kwargs.get("image_url")
        self.description = kwargs.get("description")
        self.count = kwargs.get("count")
        self.item_id = kwargs.get("item_id")

    __slots__ = (
        "image_url",
        "description",
        "count",
        "item_id",
    )


class ListedAuction(BaseCharacter, abc.Serializable):
    def __init__(self, **kwargs):
        self.auction_id = kwargs.get("auction_id")
        self.name = kwargs.get("name")
        self.level = kwargs.get("level")
        self.world = kwargs.get("world")
        self.vocation = kwargs.get("vocation")
        self.sex = kwargs.get("sex")
        self.outfit = kwargs.get("outfit")
        self.items = kwargs.get("items", [])
        self.sales_arguments = kwargs.get("sales_arguments", [])
        self.auction_start = kwargs.get("auction_start")
        self.auction_end = kwargs.get("auction_end")
        self.current_bid = kwargs.get("current_bid")

    __slots__ = (
        "auction_id",
        "name",
        "level",
        "world",
        "vocation",
        "sex",
        "outfit",
        "items",
        "sales_arguments",
        "auction_start",
        "auction_end",
        "current_bid",
    )

    @property
    def character_url(self):
        return BaseCharacter.get_url(self.name)

    @property
    def url(self):
        return self.get_url(self.auction_id)

    @classmethod
    def get_url(cls, auction_id):
        return get_tibia_url("character_trade", "currentcharactertrades", page="details", auctionid=auction_id)


class AuctionDetails(ListedAuction):
    __slots__ = (
        "hit_points",
        "mana",
        "capacity",
        "speed",
        "blessings_count",
        "mounts_count",
        "outfits_count",
        "titles",
        "skills",
        "creation_date",
        "experience",
        "gold",
        "achievement_points",
        "regular_world_transfer_available",
        "charm_expansion",
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
        "bestiary_progress"
    )

class SalesArgument(abc.Serializable):
    def __init__(self, **kwargs):
        self.category_image = kwargs.get("category_image")
        self.content = kwargs.get("content")

    __slots__ = (
        "category_image",
        "content",
    )