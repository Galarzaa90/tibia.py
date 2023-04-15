from tibiapy.models import CharacterBazaar, AuctionFilters, Auction
from tibiapy.models.bazaar import AuctionDetails


class CharacterBazaarBuilder:

    def __init__(self, **kwargs):
        self._current_page = kwargs.get("current_page") or 1
        self._total_pages = kwargs.get("total_pages") or 1
        self._results_count = kwargs.get("results_count") or 0
        self._entries = kwargs.get("entries") or []
        self._type = kwargs.get("type")
        self._filters = kwargs.get("filters")

    def current_page(self, current_page):
        self._current_page = current_page
        return self

    def total_pages(self, total_pages):
        self._total_pages = total_pages
        return self

    def results_count(self, results_count):
        self._results_count = results_count
        return self

    def entries(self, entries):
        self._entries = entries
        return self

    def add_entry(self, entry):
        self._entries.append(entry)
        return self

    def type(self, type):
        self._type = type
        return self

    def filters(self, filters):
        self._filters = filters
        return self


    def build(self):
        return CharacterBazaar(
            current_page=self._current_page,
            total_pages=self._total_pages,
            results_count=self._results_count,
            entries=self._entries,
            type=self._type,
            filters=self._filters,
        )


class AuctionBuilder:
    def __init__(self, **kwargs):
        self._auction_id = kwargs.get("auction_id")
        self._name = kwargs.get("name")
        self._level = kwargs.get("level")
        self._world = kwargs.get("world")
        self._vocation = kwargs.get("vocation")
        self._sex = kwargs.get("sex")
        self._outfit = kwargs.get("outfit")
        self._displayed_items = kwargs.get("displayed_items") or []
        self._sales_arguments = kwargs.get("sales_arguments") or []
        self._auction_start = kwargs.get("auction_start")
        self._auction_end = kwargs.get("auction_end")
        self._bid = kwargs.get("bid")
        self._bid_type = kwargs.get("bid_type")
        self._status = kwargs.get("status")

    def auction_id(self, auction_id):
        self._auction_id = auction_id
        return self

    def name(self, name):
        self._name = name
        return self

    def level(self, level):
        self._level = level
        return self

    def world(self, world):
        self._world = world
        return self

    def vocation(self, vocation):
        self._vocation = vocation
        return self

    def sex(self, sex):
        self._sex = sex
        return self

    def outfit(self, outfit):
        self._outfit = outfit
        return self

    def displayed_items(self, displayed_items):
        self._displayed_items = displayed_items
        return self

    def add_displayed_item(self, displayed_item):
        self._displayed_items.append(displayed_item)
        return self

    def sales_arguments(self, sales_arguments):
        self._sales_arguments = sales_arguments
        return self

    def add_sales_argument(self, sales_argument):
        self._sales_arguments.append(sales_argument)
        return self

    def auction_start(self, auction_start):
        self._auction_start = auction_start
        return self

    def auction_end(self, auction_end):
        self._auction_end = auction_end
        return self

    def bid(self, bid):
        self._bid = bid
        return self

    def bid_type(self, bid_type):
        self._bid_type = bid_type
        return self

    def status(self, status):
        self._status = status
        return self

    def build(self):
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

    def __init__(self, **kwargs):
        self._hit_points = kwargs.get("hit_points")
        self._mana = kwargs.get("mana")
        self._capacity = kwargs.get("capacity")
        self._speed = kwargs.get("speed")
        self._blessings_count = kwargs.get("blessings_count")
        self._mounts_count = kwargs.get("mounts_count")
        self._outfits_count = kwargs.get("outfits_count")
        self._titles_count = kwargs.get("titles_count")
        self._skills = kwargs.get("skills")
        self._creation_date = kwargs.get("creation_date")
        self._experience = kwargs.get("experience")
        self._gold = kwargs.get("gold")
        self._achievement_points = kwargs.get("achievement_points")
        self._regular_world_transfer_available_date = kwargs.get("regular_world_transfer_available_date")
        self._charm_expansion = kwargs.get("charm_expansion")
        self._available_charm_points = kwargs.get("available_charm_points")
        self._spent_charm_points = kwargs.get("spent_charm_points")
        self._prey_wildcards = kwargs.get("prey_wildcards")
        self._daily_reward_streak = kwargs.get("daily_reward_streak")
        self._hunting_task_points = kwargs.get("hunting_task_points")
        self._permanent_hunting_task_slots = kwargs.get("permanent_hunting_task_slots")
        self._permanent_prey_slots = kwargs.get("permanent_prey_slots")
        self._hirelings = kwargs.get("hirelings")
        self._hireling_jobs = kwargs.get("hireling_jobs")
        self._hireling_outfits = kwargs.get("hireling_outfits")
        self._exalted_dust = kwargs.get("exalted_dust")
        self._exalted_dust_limit = kwargs.get("exalted_dust_limit")
        self._boss_points = kwargs.get("boss_points")
        self._items = kwargs.get("items")
        self._store_items = kwargs.get("store_items")
        self._mounts = kwargs.get("mounts")
        self._store_mounts = kwargs.get("store_mounts")
        self._outfits = kwargs.get("outfits")
        self._store_outfits = kwargs.get("store_outfits")
        self._familiars = kwargs.get("familiars")
        self._blessings = kwargs.get("blessings")
        self._imbuements = kwargs.get("imbuements")
        self._charms = kwargs.get("charms")
        self._completed_cyclopedia_map_areas = kwargs.get("completed_cyclopedia_map_areas")
        self._completed_quest_lines = kwargs.get("completed_quest_lines")
        self._titles = kwargs.get("titles")
        self._achievements = kwargs.get("achievements")
        self._bestiary_progress = kwargs.get("bestiary_progress")
        self._bosstiary_progress = kwargs.get("bosstiary_progress")

    def hit_points(self, hit_points):
        self._hit_points = hit_points
        return self

    def mana(self, mana):
        self._mana = mana
        return self

    def capacity(self, capacity):
        self._capacity = capacity
        return self

    def speed(self, speed):
        self._speed = speed
        return self

    def blessings_count(self, blessings_count):
        self._blessings_count = blessings_count
        return self

    def mounts_count(self, mounts_count):
        self._mounts_count = mounts_count
        return self

    def outfits_count(self, outfits_count):
        self._outfits_count = outfits_count
        return self

    def titles_count(self, titles_count):
        self._titles_count = titles_count
        return self

    def skills(self, skills):
        self._skills = skills
        return self

    def creation_date(self, creation_date):
        self._creation_date = creation_date
        return self

    def experience(self, experience):
        self._experience = experience
        return self

    def gold(self, gold):
        self._gold = gold
        return self

    def achievement_points(self, achievement_points):
        self._achievement_points = achievement_points
        return self

    def regular_world_transfer_available_date(self, regular_world_transfer_available_date):
        self._regular_world_transfer_available_date = regular_world_transfer_available_date
        return self

    def charm_expansion(self, charm_expansion):
        self._charm_expansion = charm_expansion
        return self

    def available_charm_points(self, available_charm_points):
        self._available_charm_points = available_charm_points
        return self

    def spent_charm_points(self, spent_charm_points):
        self._spent_charm_points = spent_charm_points
        return self

    def prey_wildcards(self, prey_wildcards):
        self._prey_wildcards = prey_wildcards
        return self

    def daily_reward_streak(self, daily_reward_streak):
        self._daily_reward_streak = daily_reward_streak
        return self

    def hunting_task_points(self, hunting_task_points):
        self._hunting_task_points = hunting_task_points
        return self

    def permanent_hunting_task_slots(self, permanent_hunting_task_slots):
        self._permanent_hunting_task_slots = permanent_hunting_task_slots
        return self

    def permanent_prey_slots(self, permanent_prey_slots):
        self._permanent_prey_slots = permanent_prey_slots
        return self

    def hirelings(self, hirelings):
        self._hirelings = hirelings
        return self

    def hireling_jobs(self, hireling_jobs):
        self._hireling_jobs = hireling_jobs
        return self

    def hireling_outfits(self, hireling_outfits):
        self._hireling_outfits = hireling_outfits
        return self

    def exalted_dust(self, exalted_dust):
        self._exalted_dust = exalted_dust
        return self

    def exalted_dust_limit(self, exalted_dust_limit):
        self._exalted_dust_limit = exalted_dust_limit
        return self

    def boss_points(self, boss_points):
        self._boss_points = boss_points
        return self

    def items(self, items):
        self._items = items
        return self

    def store_items(self, store_items):
        self._store_items = store_items
        return self

    def mounts(self, mounts):
        self._mounts = mounts
        return self

    def store_mounts(self, store_mounts):
        self._store_mounts = store_mounts
        return self

    def outfits(self, outfits):
        self._outfits = outfits
        return self

    def store_outfits(self, store_outfits):
        self._store_outfits = store_outfits
        return self

    def familiars(self, familiars):
        self._familiars = familiars
        return self

    def blessings(self, blessings):
        self._blessings = blessings
        return self

    def imbuements(self, imbuements):
        self._imbuements = imbuements
        return self

    def charms(self, charms):
        self._charms = charms
        return self

    def completed_cyclopedia_map_areas(self, completed_cyclopedia_map_areas):
        self._completed_cyclopedia_map_areas = completed_cyclopedia_map_areas
        return self

    def completed_quest_lines(self, completed_quest_lines):
        self._completed_quest_lines = completed_quest_lines
        return self

    def titles(self, titles):
        self._titles = titles
        return self

    def achievements(self, achievements):
        self._achievements = achievements
        return self

    def bestiary_progress(self, bestiary_progress):
        self._bestiary_progress = bestiary_progress
        return self

    def bosstiary_progress(self, bosstiary_progress):
        self._bosstiary_progress = bosstiary_progress
        return self

    def build(self):
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
        )
