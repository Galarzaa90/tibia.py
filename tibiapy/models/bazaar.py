import datetime
from typing import Optional, List, Type, Dict

from pydantic import BaseModel, PrivateAttr

from tibiapy import PvpTypeFilter, BattlEyeTypeFilter, VocationAuctionFilter, SkillFilter, AuctionSearchType, \
    AuctionOrderBy, AuctionOrder, BazaarType, Vocation, Sex, BidType, AuctionStatus
from tibiapy.models.base import BaseCharacter
from tibiapy.utils import get_tibia_url

__all__ = (
    'AchievementEntry',
    'AuctionFilters',
    'BestiaryEntry',
    'BlessingEntry',
    'CharacterBazaar',
    'CharmEntry',
    'DisplayImage',
    'DisplayItem',
    'DisplayMount',
    'DisplayOutfit',
    'OutfitImage',
    'PaginatedSummary',
    'ItemSummary',
    'Mounts',
    'Familiars',
    'Outfits',
    'SalesArgument',
    'SkillEntry',
    'AuctionEntry',
    'Auction',
)

class AchievementEntry(BaseModel):
    """An unlocked achievement by the character."""


    name: str
    """The name of the achievement."""
    secret: bool
    """Whether the achievement is secret or not."""


class AuctionFilters(BaseModel):
    """The auction filters available in the auctions section.

        All attributes are optional.
    """

    world: Optional[str] = None
    """The character's world to show characters for."""
    pvp_type: Optional[PvpTypeFilter] = None
    """The PvP type of the character's worlds to show."""
    battleye: Optional[BattlEyeTypeFilter] = None
    """The type of BattlEye protection of the character's worlds to show."""
    vocation: Optional[VocationAuctionFilter] = None
    """The character vocation to show results for."""
    min_level: Optional[int] = None
    """The minimum level to display."""
    max_level: Optional[int] = None
    """The maximum level to display."""
    skill: Optional[SkillFilter] = None
    """The skill to filter by its level range."""
    min_skill_level: Optional[int] = None
    """The minimum skill level of the selected :attr:`skill` to display."""
    max_skill_level: Optional[int] = None
    """The maximum skill level of the selected :attr:`skill` to display."""
    order_by: Optional[AuctionOrderBy] = None
    order: Optional[AuctionOrder] = None
    search_string: Optional[str] = None
    """The search term to filter out auctions."""
    search_type: Optional[AuctionSearchType] = None
    """The type of search to use. Defines the behaviour of :py:attr:`search_string`."""
    available_worlds: List[str] = []
    """The list of available worlds to select to filter."""

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


class BestiaryEntry(BaseModel):
    """The bestiary progress for a specific creature."""

    name: str
    """The name of the creature."""
    kills: int
    """The number of kills of this creature the player has done."""
    step: int
    """The current step to unlock this creature the character is in, where 4 is fully unlocked."""

    @property
    def completed(self):
        """:class:`bool`: Whether the entry is completed or not."""
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


class DisplayImage(BaseModel):
    """An image displayed in the auction."""

    image_url: str
    """The URL to the image."""
    name: str
    """The element's name."""

class DisplayItem(DisplayImage):
    """Represents an item displayed on an auction, or the character's items in the auction detail."""

    image_url: str
    """The URL to the item's image."""
    name: str
    """The item's name."""
    description: Optional[str]
    """The item's description, if any."""
    count: int = 1
    """The item's count."""
    item_id: int
    """The item's client id."""
    tier: int = 0
    """The item's tier."""

class DisplayMount(DisplayImage):
    """Represents a mount owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The mount's name."""
    mount_id: int
    """The internal ID of the mount."""


class DisplayOutfit(DisplayImage):
    """Represents a outfit owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The outfit's name."""
    outfit_id: int
    """The internal ID of the outfit."""

class DisplayFamiliar(DisplayImage):
    """Represents a familiar owned or unlocked by the character."""

    image_url: str
    """The URL to the image."""
    name: str
    """The familiar's name."""
    familiar_id: int
    """The internal ID of the familiar."""

class OutfitImage(BaseModel):
    """The image of the outfit currently being worn by the character."""


    image_url: str
    """The URL of the image."""
    outfit_id: int
    """The ID of the outfit."""
    addons: int
    """The addons displayed in the outfit."""

class PaginatedSummary(BaseModel):
    """Represents a paginated summary in the character auction section."""


    page: int
    """The current page being displayed."""
    total_pages: int
    """The total number of pages."""
    results: int
    """The total number of results."""
    entries: list = []
    """The entries."""
    fully_fetched: bool = False
    """Whether the summary was fetched completely, including all other pages."""

    _entry_class: Type = PrivateAttr(None)


class ItemSummary(PaginatedSummary):
    """Items in a character's inventory and depot."""


    entries: List[DisplayItem] = []
    """The character's items."""

    _entry_class: Type = DisplayItem


class Mounts(PaginatedSummary):
    entries: List[DisplayMount] = []
    """The character's mounts."""

    _entry_class: Type = DisplayMount


class Familiars(PaginatedSummary):
    """The familiars the character has unlocked or purchased."""

    entries: List[DisplayFamiliar] = []
    """The character's faimiliars."""

    _entry_class: Type = DisplayFamiliar

class Outfits(PaginatedSummary):
    """The outfits the character has unlocked or purchased."""

    entries: List[DisplayOutfit] = []
    """The character's faimiliars."""

    _entry_class: Type = DisplayOutfit


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

class AuctionEntry(BaseCharacter):
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
    displayed_items: List[DisplayItem]
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

    @property
    def character_url(self):
        """:class:`str`: The URL of the character's information page on Tibia.com."""
        return BaseCharacter.get_url(self.name)

    @property
    def url(self):
        """:class:`str`: The URL to this auction's detail page on Tibia.com."""
        return self.get_url(self.auction_id)

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


class Auction(AuctionEntry):
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


class CharacterBazaar(BaseModel):
    """Represents the char bazaar."""

    page: int
    """The page being currently viewed."""
    total_pages: int
    """The total number of pages available."""
    results_count: int
    """The number of auctions listed."""
    entries: List[AuctionEntry]
    """The auctions displayed."""
    type: BazaarType
    """The type of auctions being displayed, either current or auction history."""
    filters: Optional[AuctionFilters] = None
    """The currently set filtering options."""

    @property
    def url(self):
        """:class:`str`: Get the URL to the bazaar."""
        return self.get_auctions_history_url(self.page) if self.type == BazaarType.HISTORY else \
            self.get_current_auctions_url(self.page, self.filters)

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