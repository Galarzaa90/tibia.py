"""Models relatd to the character bazaar."""
import datetime
from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, TypeVar

from tibiapy.enums import (AuctionBattlEyeFilter, AuctionOrderBy, AuctionOrderDirection, AuctionSearchType,
                           AuctionSkillFilter, AuctionStatus, AuctionVocationFilter, BazaarType, BidType, PvpTypeFilter,
                           Sex, Vocation)
from tibiapy.models import BaseModel
from tibiapy.models.pagination import AjaxPaginator, PaginatedWithUrl

__all__ = (
    "AchievementEntry",
    "Auction",
    "AuctionDetails",
    "AuctionFilters",
    "BestiaryEntry",
    "BlessingEntry",
    "CharacterBazaar",
    "CharmEntry",
    "FamiliarEntry",
    "Familiars",
    "ItemEntry",
    "ItemSummary",
    "MountEntry",
    "Mounts",
    "OutfitEntry",
    "OutfitImage",
    "Outfits",
    "RevealedGem",
    "SalesArgument",
    "SkillEntry",
)

from tibiapy.urls import get_auction_url, get_bazaar_url, get_character_url


class AchievementEntry(BaseModel):
    """An unlocked achievement by the character."""

    name: str
    """The name of the achievement."""
    is_secret: bool
    """Whether the achievement is secret or not."""


class AuctionFilters(BaseModel):
    """The auction filters available in the auctions section.

    All attributes are optional.
    """

    world: Optional[str] = None
    """The character's world to show characters for."""
    pvp_type: Optional[PvpTypeFilter] = None
    """The PvP type of the character's worlds to show."""
    battleye: Optional[AuctionBattlEyeFilter] = None
    """The type of BattlEye protection of the character's worlds to show."""
    vocation: Optional[AuctionVocationFilter] = None
    """The character vocation to show results for."""
    min_level: Optional[int] = None
    """The minimum level to display."""
    max_level: Optional[int] = None
    """The maximum level to display."""
    skill: Optional[AuctionSkillFilter] = None
    """The skill to filter by its level range."""
    min_skill_level: Optional[int] = None
    """The minimum skill level of the selected :attr:`skill` to display."""
    max_skill_level: Optional[int] = None
    """The maximum skill level of the selected :attr:`skill` to display."""
    order_by: Optional[AuctionOrderBy] = None
    """The column or value to order by."""
    order: Optional[AuctionOrderDirection] = None
    """The ordering direction for the results."""
    search_string: Optional[str] = None
    """The search term to filter out auctions."""
    search_type: Optional[AuctionSearchType] = None
    """The type of search to use. Defines the behaviour of :py:attr:`search_string`."""
    available_worlds: List[str] = []
    """The list of available worlds to select to filter."""

    @property
    def query_params(self) -> Dict[str, str]:
        """The query parameters representing this filter."""
        params = {
            "filter_profession": self.vocation.value if self.vocation is not None else None,
            "filter_levelrangefrom": self.min_level,
            "filter_levelrangeto": self.max_level,
            "filter_world": self.world,
            "filter_worldpvptype": self.pvp_type.value if self.pvp_type is not None else None,
            "filter_worldbattleyestate": self.battleye.value if self.battleye is not None else None,
            "filter_skillid": self.skill.value if self.skill is not None else None,
            "filter_skillrangefrom": self.min_skill_level,
            "filter_skillrangeto": self.max_skill_level,
            "order_column": self.order_by.value if self.order_by is not None else None,
            "order_direction": self.order.value if self.order is not None else None,
            "searchstring": self.search_string,
            "searchtype": self.search_type.value if self.search_type is not None else None,
        }
        return {k: v for k, v in params.items() if v is not None}


class BestiaryEntry(BaseModel):
    """The bestiary progress for a specific creature."""

    name: str
    """The name of the creature."""
    kills: int
    """The number of kills of this creature the player has done."""
    step: int
    """The current step to unlock this creature the character is in, where 4 is fully unlocked."""

    @property
    def is_completed(self) -> bool:
        """Whether the entry is completed or not."""
        return self.step == 4


class BlessingEntry(BaseModel):
    """A character's blessings."""

    name: str
    """The name of the blessing."""
    amount: int
    """The amount of blessing charges the character has."""


class CharmEntry(BaseModel):
    """An unlocked charm by the character."""

    name: str
    """The name of the charm."""
    cost: int
    """The cost of the charm in charm points."""


class BaseOutfit(BaseModel):
    """A base outfit displayed in auctions."""

    outfit_id: int
    """The internal ID of the outfit."""
    addons: int
    """The selected or unlocked addons."""
    image_url: str


class DisplayImage(BaseModel):
    """An image displayed in the auction."""

    image_url: str
    """The URL to the image."""
    name: str
    """The element's name."""


class ItemEntry(DisplayImage):
    """Represents an item displayed on an auction, or the character's items in the auction detail."""

    image_url: str
    """The URL to the item's image."""
    name: str
    """The item's name."""
    description: Optional[str] = None
    """The item's description, if any."""
    count: int = 1
    """The item's count."""
    item_id: int
    """The item's client id."""
    tier: int = 0
    """The item's tier."""


class MountEntry(DisplayImage):
    """Represents a mount owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The mount's name."""
    mount_id: int
    """The internal ID of the mount."""


class OutfitEntry(DisplayImage, BaseOutfit):
    """Represents an outfit owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The outfit's name."""
    outfit_id: int
    """The internal ID of the outfit."""


class FamiliarEntry(DisplayImage):
    """Represents a familiar owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The familiar's name."""
    familiar_id: int
    """The internal ID of the familiar."""


class OutfitImage(BaseOutfit):
    """The image of the outfit currently being worn by the character."""

    image_url: str
    """The URL of the image."""
    outfit_id: int
    """The ID of the outfit."""
    addons: int
    """The addons displayed in the outfit."""


T = TypeVar("T", bound=DisplayImage)


class AuctionSummary(AjaxPaginator[T], Generic[T], ABC):
    def get_by_name(self, name: str):
        """Get an entry by its name.

        Parameters
        ----------
        name: :class:`str`
            The name of the entry, case-insensitive.

        Returns
        -------
        :class:`object`:
            The entry matching the name.
        """
        return next((e for e in self.entries if e.name.lower() == name.lower()), None)

    def search(self, value: str):
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

    @abstractmethod
    def get_by_id(self, entry_id: int):
        ...


class ItemSummary(AuctionSummary[ItemEntry]):
    """Items in a character's inventory and depot."""

    def get_by_id(self, entry_id: int) -> Optional[ItemEntry]:
        """Get an item by its item id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the item.

        Returns
        -------
        :class:`ItemEntry`
            The item matching the id.
        """
        return next((e for e in self.entries if e.item_id == entry_id), None)


class Mounts(AuctionSummary[MountEntry]):
    """The mounts the character has unlocked or purchased."""

    def get_by_id(self, entry_id: int) -> Optional[MountEntry]:
        """Get a mount by its mount id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the mount.

        Returns
        -------
        :class:`MountEntry`
            The mount matching the id.
        """
        return next((e for e in self.entries if e.mount_id == entry_id), None)


class Familiars(AuctionSummary[FamiliarEntry]):
    """The familiars the character has unlocked or purchased."""

    def get_by_id(self, entry_id: int) -> Optional[FamiliarEntry]:
        """Get a familiar by its familiar id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the familiar.

        Returns
        -------
        :class:`FamiliarEntry`
            The familiar matching the id.
        """
        return next((e for e in self.entries if e.familiar_id == entry_id), None)


class Outfits(AuctionSummary[OutfitEntry]):
    """The outfits the character has unlocked or purchased."""

    def get_by_id(self, entry_id: int) -> Optional[OutfitEntry]:
        """Get an outfit by its outfit id.

        Parameters
        ----------
        entry_id: :class:`int`
            The ID of the outfit.

        Returns
        -------
        :class:`OutfitEntry`
            The outfit matching the id.
        """
        return next((e for e in self.entries if e.outfit_id == entry_id), None)


class SalesArgument(BaseModel):
    """Represents a sales argument.

    Sales arguments can be selected when creating an auction, and allow the user to highlight certain
    character features in the auction listing.
    """

    category_id: int
    category_image: str
    """The URL to the category icon."""
    content: str
    """The content of the sales argument."""


class SkillEntry(BaseModel):
    """Represents the character's skills."""

    name: str
    """The name of the skill."""
    level: int
    """The current level."""
    progress: float
    """The percentage of progress for the next level."""


class RevealedGem(BaseModel):
    """A gem that has been revealed for the character."""

    gem_type: str
    """The type of gem."""
    mods: List[str]
    """The mods or effects the gem has."""


class AuctionDetails(BaseModel):
    """The details of an auction."""

    hit_points: int
    """The hit points of the character."""
    mana: int
    """The mana points of the character."""
    capacity: int
    """The character's capacity in ounces."""
    speed: int
    """The character's speed."""
    blessings_count: int
    """The number of blessings the character has."""
    mounts_count: int
    """The number of mounts the character has."""
    outfits_count: int
    """The number of outfits the character has."""
    titles_count: int
    """The number of titles the character has."""
    skills: List[SkillEntry]
    """The current skills of the character."""
    creation_date: datetime.datetime
    """The date when the character was created."""
    experience: int
    """The total experience of the character."""
    gold: int
    """The total amount of gold the character has."""
    achievement_points: int
    """The number of achievement points of the character."""
    regular_world_transfer_available_date: Optional[datetime.datetime] = None
    """The date after regular world transfers will be available to purchase and use.
    :obj:`None` indicates it is available immediately."""
    charm_expansion: bool
    """Whether the character has a charm expansion or not."""
    available_charm_points: int
    """The amount of charm points the character has available to spend."""
    spent_charm_points: int
    """The total charm points the character has spent."""
    prey_wildcards: int
    """The number of Prey Wildcards the character has."""
    daily_reward_streak: int
    """The current daily reward streak."""
    hunting_task_points: int
    permanent_hunting_task_slots: int
    """The number of hunting task slots."""
    permanent_prey_slots: int
    """The number of prey slots."""
    hirelings: int
    """The number of hirelings the character has."""
    hireling_jobs: int
    """The number of hireling jobs the character has."""
    hireling_outfits: int
    """The number of hireling outfits the character has."""
    exalted_dust: int
    """The amount of exalted dust the character has."""
    exalted_dust_limit: int
    """The dust limit of the character."""
    boss_points: int
    """The boss points of the character."""
    bonus_promotion_points: int
    """The bonus promotion points of the character."""
    items: ItemSummary
    """The items the character has across inventory, depot and item stash."""
    store_items: ItemSummary
    """The store items the character has."""
    mounts: Mounts
    """The mounts the character has unlocked."""
    store_mounts: Mounts
    """The mounts the character has purchased from the store."""
    outfits: Outfits
    """The outfits the character has unlocked."""
    store_outfits: Outfits
    """The outfits the character has purchased from the store."""
    familiars: Familiars
    """The familiars the character has purchased or unlocked."""
    blessings: List[BlessingEntry]
    """The blessings the character has."""
    imbuements: List[str]
    """The imbuements the character has unlocked access to."""
    charms: List[CharmEntry]
    """The charms the character has unlocked."""
    completed_cyclopedia_map_areas: List[str]
    """The cyclopedia map areas that the character has fully discovered."""
    completed_quest_lines: List[str]
    """The quest lines the character has fully completed."""
    titles: List[str]
    """The titles the character has unlocked."""
    achievements: List[AchievementEntry]
    """The achievements the character has unlocked."""
    bestiary_progress: List[BestiaryEntry]
    """The bestiary progress of the character."""
    bosstiary_progress: List[BestiaryEntry]
    """The bosstiary progress of the character."""
    revealed_gems: List[RevealedGem]
    """The gems that have been revealed by the character."""

    @property
    def completed_bestiary_entries(self) -> List[BestiaryEntry]:
        """Get a list of completed bestiary entries."""
        return [e for e in self.bestiary_progress if e.is_completed]

    @property
    def regular_world_transfer_available(self) -> bool:
        """Whether regular world transfers are available immediately for this character."""
        return self.regular_world_transfer_available_date is None

    @property
    def skills_map(self) -> Dict[str, SkillEntry]:
        """A mapping of skills by their name."""
        return {skill.name: skill for skill in self.skills}


class Auction(BaseModel):
    """Represents an auction in the list, containing the summary."""

    auction_id: int
    """The internal id of the auction."""
    name: str
    """The name of the character."""
    level: int
    """The level of the character."""
    world: str
    """The world the character is in."""
    vocation: Vocation
    """The vocation of the character."""
    sex: Sex
    """The sex of the character."""
    outfit: OutfitImage
    """The current outfit selected by the user."""
    displayed_items: List[ItemEntry]
    """The items selected to be displayed."""
    sales_arguments: List[SalesArgument]
    """The sale arguments selected for the auction."""
    auction_start: datetime.datetime
    """The date when the auction started."""
    auction_end: datetime.datetime
    """The date when the auction ends."""
    bid: int
    """The current bid in Tibia Coins."""
    bid_type: BidType
    """The type of the auction's bid."""
    status: AuctionStatus
    """The current status of the auction."""
    details: Optional[AuctionDetails] = None
    """The auction's details."""

    @property
    def character_url(self) -> str:
        """The URL of the character's information page on Tibia.com."""
        return get_character_url(self.name)

    @property
    def url(self) -> str:
        """The URL to this auction's detail page on Tibia.com."""
        return get_auction_url(self.auction_id)


class CharacterBazaar(PaginatedWithUrl[Auction]):
    """Represents the char bazaar."""

    type: BazaarType
    """The type of auctions being displayed, either current or auction history."""
    filters: Optional[AuctionFilters] = None
    """The currently set filtering options."""

    def get_page_url(self, page: int) -> str:
        """Get the URL to a given page of the bazaar.

        Parameters
        ----------
        page: :class:`int`
            The desired page.

        Returns
        -------
        :class:`str`
            The URL to the desired page.
        """
        return get_bazaar_url(self.type, page, self.filters)

    @property
    def url(self) -> str:
        """The URL to the Character Bazaar with the current parameters."""
        return get_bazaar_url(self.type, self.current_page, self.filters)
