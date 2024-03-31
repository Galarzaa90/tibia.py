from __future__ import annotations


from typing import List, Optional, TYPE_CHECKING

from tibiapy.models import Auction, CharacterBazaar
from tibiapy.models.bazaar import AuctionDetails, RevealedGem

if TYPE_CHECKING:
    import datetime
    from typing_extensions import Self
    from tibiapy.enums import BazaarType, Vocation, Sex, BidType, AuctionStatus
    from tibiapy.models import (AuctionFilters, OutfitImage, ItemEntry, SalesArgument, SkillEntry, ItemSummary, Mounts,
                                Outfits, Familiars, BlessingEntry, CharmEntry, AchievementEntry, BestiaryEntry)


class CharacterBazaarBuilder:
    def __init__(self):
        self._current_page = 1
        self._total_pages = 1
        self._results_count = 0
        self._entries = []
        self._type = None
        self._filters = None

    def current_page(self, current_page: int) -> Self:
        self._current_page = current_page
        return self

    def total_pages(self, total_pages: int) -> Self:
        self._total_pages = total_pages
        return self

    def results_count(self, results_count: int) -> Self:
        self._results_count = results_count
        return self

    def entries(self, entries: List[Auction]) -> Self:
        self._entries = entries
        return self

    def add_entry(self, entry: Auction) -> Self:
        self._entries.append(entry)
        return self

    def type(self, type: BazaarType) -> Self:
        self._type = type
        return self

    def filters(self, filters: AuctionFilters) -> Self:
        self._filters = filters
        return self

    def build(self) -> CharacterBazaar:
        return CharacterBazaar(
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
            entries=self._entries,
            type=self._type,
            filters=self._filters,
        )


class AuctionBuilder:
    def __init__(self):
        self._auction_id = None
        self._name = None
        self._level = None
        self._world = None
        self._vocation = None
        self._sex = None
        self._outfit = None
        self._displayed_items = []
        self._sales_arguments = []
        self._auction_start = None
        self._auction_end = None
        self._bid = None
        self._bid_type = None
        self._status = None

    def auction_id(self, auction_id: int) -> Self:
        self._auction_id = auction_id
        return self

    def name(self, name: str) -> Self:
        self._name = name
        return self

    def level(self, level: int) -> Self:
        self._level = level
        return self

    def world(self, world: str) -> Self:
        self._world = world
        return self

    def vocation(self, vocation: Vocation) -> Self:
        self._vocation = vocation
        return self

    def sex(self, sex: Sex) -> Self:
        self._sex = sex
        return self

    def outfit(self, outfit: OutfitImage) -> Self:
        self._outfit = outfit
        return self

    def displayed_items(self, displayed_items: List[ItemEntry]) -> Self:
        self._displayed_items = displayed_items
        return self

    def add_displayed_item(self, displayed_item: ItemEntry) -> Self:
        self._displayed_items.append(displayed_item)
        return self

    def sales_arguments(self, sales_arguments: List[SalesArgument]) -> Self:
        self._sales_arguments = sales_arguments
        return self

    def add_sales_argument(self, sales_argument: SalesArgument) -> Self:
        self._sales_arguments.append(sales_argument)
        return self

    def auction_start(self, auction_start: datetime.datetime) -> Self:
        self._auction_start = auction_start
        return self

    def auction_end(self, auction_end: datetime.datetime) -> Self:
        self._auction_end = auction_end
        return self

    def bid(self, bid: int) -> Self:
        self._bid = bid
        return self

    def bid_type(self, bid_type: BidType) -> Self:
        self._bid_type = bid_type
        return self

    def status(self, status: AuctionStatus) -> Self:
        self._status = status
        return self

    def build(self) -> Auction:
        return Auction(
            auction_id=self._auction_id,
            name=self._name,
            level=self._level,
            world=self._world,
            vocation=self._vocation,
            sex=self._sex,
            outfit=self._outfit,
            displayed_items=self._displayed_items,
            sales_arguments=self._sales_arguments,
            auction_start=self._auction_start,
            auction_end=self._auction_end,
            bid=self._bid,
            bid_type=self._bid_type,
            status=self._status,
        )


class AuctionDetailsBuilder:

    def __init__(self):
        self._hit_points = None
        self._mana = None
        self._capacity = None
        self._speed = None
        self._blessings_count = None
        self._mounts_count = None
        self._outfits_count = None
        self._titles_count = None
        self._skills = None
        self._creation_date = None
        self._experience = None
        self._gold = None
        self._achievement_points = None
        self._regular_world_transfer_available_date = None
        self._charm_expansion = None
        self._available_charm_points = None
        self._spent_charm_points = None
        self._prey_wildcards = None
        self._daily_reward_streak = None
        self._hunting_task_points = None
        self._permanent_hunting_task_slots = None
        self._permanent_prey_slots = None
        self._hirelings = None
        self._hireling_jobs = None
        self._hireling_outfits = None
        self._exalted_dust = None
        self._exalted_dust_limit = None
        self._boss_points = None
        self._bonus_promotion_points = None
        self._items = None
        self._store_items = None
        self._mounts = None
        self._store_mounts = None
        self._outfits = None
        self._store_outfits = None
        self._familiars = None
        self._blessings = None
        self._imbuements = None
        self._charms = None
        self._completed_cyclopedia_map_areas = None
        self._completed_quest_lines = None
        self._titles = None
        self._achievements = None
        self._bestiary_progress = None
        self._bosstiary_progress = None
        self._revealed_gems = []

    def hit_points(self, hit_points: int) -> Self:
        self._hit_points = hit_points
        return self

    def mana(self, mana: int) -> Self:
        self._mana = mana
        return self

    def capacity(self, capacity: int) -> Self:
        self._capacity = capacity
        return self

    def speed(self, speed: int) -> Self:
        self._speed = speed
        return self

    def blessings_count(self, blessings_count: int) -> Self:
        self._blessings_count = blessings_count
        return self

    def mounts_count(self, mounts_count: int) -> Self:
        self._mounts_count = mounts_count
        return self

    def outfits_count(self, outfits_count: int) -> Self:
        self._outfits_count = outfits_count
        return self

    def titles_count(self, titles_count: int) -> Self:
        self._titles_count = titles_count
        return self

    def skills(self, skills: List[SkillEntry]) -> Self:
        self._skills = skills
        return self

    def creation_date(self, creation_date: datetime.datetime) -> Self:
        self._creation_date = creation_date
        return self

    def experience(self, experience: int) -> Self:
        self._experience = experience
        return self

    def gold(self, gold: int) -> Self:
        self._gold = gold
        return self

    def achievement_points(self, achievement_points: int) -> Self:
        self._achievement_points = achievement_points
        return self

    def regular_world_transfer_available_date(
            self,
            regular_world_transfer_available_date: Optional[datetime.datetime],
    ) -> Self:
        self._regular_world_transfer_available_date = regular_world_transfer_available_date
        return self

    def charm_expansion(self, charm_expansion: bool) -> Self:
        self._charm_expansion = charm_expansion
        return self

    def available_charm_points(self, available_charm_points: int) -> Self:
        self._available_charm_points = available_charm_points
        return self

    def spent_charm_points(self, spent_charm_points: int) -> Self:
        self._spent_charm_points = spent_charm_points
        return self

    def prey_wildcards(self, prey_wildcards: int) -> Self:
        self._prey_wildcards = prey_wildcards
        return self

    def daily_reward_streak(self, daily_reward_streak: int) -> Self:
        self._daily_reward_streak = daily_reward_streak
        return self

    def hunting_task_points(self, hunting_task_points: int) -> Self:
        self._hunting_task_points = hunting_task_points
        return self

    def permanent_hunting_task_slots(self, permanent_hunting_task_slots: int) -> Self:
        self._permanent_hunting_task_slots = permanent_hunting_task_slots
        return self

    def permanent_prey_slots(self, permanent_prey_slots: int) -> Self:
        self._permanent_prey_slots = permanent_prey_slots
        return self

    def hirelings(self, hirelings: int) -> Self:
        self._hirelings = hirelings
        return self

    def hireling_jobs(self, hireling_jobs: int) -> Self:
        self._hireling_jobs = hireling_jobs
        return self

    def hireling_outfits(self, hireling_outfits: int) -> Self:
        self._hireling_outfits = hireling_outfits
        return self

    def exalted_dust(self, exalted_dust: int) -> Self:
        self._exalted_dust = exalted_dust
        return self

    def exalted_dust_limit(self, exalted_dust_limit: int) -> Self:
        self._exalted_dust_limit = exalted_dust_limit
        return self

    def boss_points(self, boss_points: int) -> Self:
        self._boss_points = boss_points
        return self

    def bonus_promotion_points(self, bonus_promotion_points: int) -> Self:
        self._bonus_promotion_points = bonus_promotion_points
        return self

    def items(self, items: ItemSummary) -> Self:
        self._items = items
        return self

    def store_items(self, store_items: ItemSummary) -> Self:
        self._store_items = store_items
        return self

    def mounts(self, mounts: Mounts) -> Self:
        self._mounts = mounts
        return self

    def store_mounts(self, store_mounts: Mounts) -> Self:
        self._store_mounts = store_mounts
        return self

    def outfits(self, outfits: Outfits) -> Self:
        self._outfits = outfits
        return self

    def store_outfits(self, store_outfits: Outfits) -> Self:
        self._store_outfits = store_outfits
        return self

    def familiars(self, familiars: Familiars) -> Self:
        self._familiars = familiars
        return self

    def blessings(self, blessings: List[BlessingEntry]) -> Self:
        self._blessings = blessings
        return self

    def imbuements(self, imbuements: List[str]) -> Self:
        self._imbuements = imbuements
        return self

    def charms(self, charms: List[CharmEntry]) -> Self:
        self._charms = charms
        return self

    def completed_cyclopedia_map_areas(self, completed_cyclopedia_map_areas: List[str]) -> Self:
        self._completed_cyclopedia_map_areas = completed_cyclopedia_map_areas
        return self

    def completed_quest_lines(self, completed_quest_lines: List[str]) -> Self:
        self._completed_quest_lines = completed_quest_lines
        return self

    def titles(self, titles: List[str]) -> Self:
        self._titles = titles
        return self

    def achievements(self, achievements: List[AchievementEntry]) -> Self:
        self._achievements = achievements
        return self

    def bestiary_progress(self, bestiary_progress: List[BestiaryEntry]) -> Self:
        self._bestiary_progress = bestiary_progress
        return self

    def bosstiary_progress(self, bosstiary_progress: List[BestiaryEntry]) -> Self:
        self._bosstiary_progress = bosstiary_progress
        return self

    def add_revealed_gem(self, gem: RevealedGem) -> Self:
        self._revealed_gems.append(gem)
        return self

    def build(self) -> AuctionDetails:
        return AuctionDetails(
            hit_points=self._hit_points,
            mana=self._mana,
            capacity=self._capacity,
            speed=self._speed,
            blessings_count=self._blessings_count,
            mounts_count=self._mounts_count,
            outfits_count=self._outfits_count,
            titles_count=self._titles_count,
            skills=self._skills,
            creation_date=self._creation_date,
            experience=self._experience,
            gold=self._gold,
            achievement_points=self._achievement_points,
            regular_world_transfer_available_date=self._regular_world_transfer_available_date,
            charm_expansion=self._charm_expansion,
            available_charm_points=self._available_charm_points,
            spent_charm_points=self._spent_charm_points,
            prey_wildcards=self._prey_wildcards,
            daily_reward_streak=self._daily_reward_streak,
            hunting_task_points=self._hunting_task_points,
            permanent_hunting_task_slots=self._permanent_hunting_task_slots,
            permanent_prey_slots=self._permanent_prey_slots,
            hirelings=self._hirelings,
            hireling_jobs=self._hireling_jobs,
            hireling_outfits=self._hireling_outfits,
            exalted_dust=self._exalted_dust,
            exalted_dust_limit=self._exalted_dust_limit,
            boss_points=self._boss_points,
            bonus_promotion_points=self._bonus_promotion_points,
            items=self._items,
            store_items=self._store_items,
            mounts=self._mounts,
            store_mounts=self._store_mounts,
            outfits=self._outfits,
            store_outfits=self._store_outfits,
            familiars=self._familiars,
            blessings=self._blessings,
            imbuements=self._imbuements,
            charms=self._charms,
            completed_cyclopedia_map_areas=self._completed_cyclopedia_map_areas,
            completed_quest_lines=self._completed_quest_lines,
            titles=self._titles,
            achievements=self._achievements,
            bestiary_progress=self._bestiary_progress,
            bosstiary_progress=self._bosstiary_progress,
            revealed_gems=self._revealed_gems,
        )
