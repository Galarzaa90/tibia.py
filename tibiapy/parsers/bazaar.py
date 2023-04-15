"""Contains all classes related to the Character Bazaar sections in Tibia.com"""
import logging
import re
import urllib.parse
from typing import Dict, List

import bs4

from tibiapy import InvalidContent, Sex, Vocation, abc
from tibiapy.builders.bazaar import CharacterBazaarBuilder, AuctionBuilder, AuctionDetailsBuilder
from tibiapy.enums import (AuctionOrder, AuctionOrderBy, AuctionSearchType, AuctionStatus, BattlEyeTypeFilter,
                           BazaarType, BidType, PvpTypeFilter, SkillFilter, VocationAuctionFilter)
from tibiapy.models.bazaar import AuctionFilters, DisplayImage, DisplayItem, OutfitImage, SalesArgument, \
    SkillEntry, BlessingEntry, CharmEntry, AchievementEntry, BestiaryEntry, PaginatedSummary, DisplayMount, ItemSummary, \
    Mounts, Familiars, Outfits, DisplayFamiliar, DisplayOutfit, CharacterBazaar, Auction
from tibiapy.utils import (convert_line_breaks, parse_form_data, parse_integer, parse_pagination,
                           parse_tibia_datetime, parse_tibiacom_content, try_enum)

results_pattern = re.compile(r'Results: (\d+)')
char_info_regex = re.compile(r'Level: (\d+) \| Vocation: ([\w\s]+)\| (\w+) \| World: (\w+)')
id_addon_regex = re.compile(r'(\d+)_(\d)\.gif')
id_regex = re.compile(r'(\d+).(?:gif|png)')
description_regex = re.compile(r'"(?:an?\s)?([^"]+)"')
amount_regex = re.compile(r'([\d,]+)x')
tier_regex = re.compile(r"(.*)\s\(tier (\d)\)")

log = logging.getLogger("tibiapy")

class AuctionFiltersParser:
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
        forms = table.select("form")
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


class CharacterBazaarParser:
    @classmethod
    def from_content(cls, content) -> CharacterBazaar:
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
            content_table = parsed_content.select_one("div.BoxContent")
            tables = content_table.select("div.TableContainer")
            filter_table = None
            if len(tables) == 1:
                auctions_table = tables[0]
            else:
                filter_table, auctions_table, *_ = tables

            builder = CharacterBazaarBuilder()
            builder.type(BazaarType.CURRENT if filter_table else BazaarType.HISTORY)

            if filter_table:
                builder.filters(AuctionFiltersParser._parse_filter_table(filter_table))

            if page_navigation_row := parsed_content.select_one("td.PageNavigation"):
                page, total_pages, results_count = parse_pagination(page_navigation_row)
                builder.current_page(page).total_pages(total_pages).results_count(results_count)

            auction_rows = auctions_table.select("div.Auction")
            for auction_row in auction_rows:
                auction = AuctionParser._parse_auction(auction_row)

                builder.add_entry(auction)
            return builder.build()
        except (ValueError, IndexError) as e:
            raise InvalidContent("content does not belong to the bazaar at Tibia.com", original=e) from e


class DisplayImageParser:

    @classmethod
    def _parse_image_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None
        return DisplayImage(image_url=img_tag["src"], name=description)


class DisplayItemParser:

    @classmethod
    def _parse_image_box(cls, item_box: bs4.Tag):
        title_text = item_box["title"]
        img_tag = item_box.select_one("img")
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


class DisplayMountParser(DisplayImageParser):
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
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None
        mount = DisplayMount(image_url=img_tag["src"], name=description, mount_id=0)
        m = id_regex.search(mount.image_url)
        if m:
            mount.mount_id = int(m.group(1))
        return mount


class DisplayOutfitParser(DisplayImageParser):

    @classmethod
    def _parse_image_box(cls, item_box):
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None
        outfit = DisplayOutfit(image_url=img_tag["src"], name=description, outfit_id=0)
        name = outfit.name.split("(")[0].strip()
        outfit.name = name
        m = id_addon_regex.search(outfit.image_url)
        if m:
            outfit.outfit_id = int(m.group(1))
            # outfit.addons = int(m.group(2))
        return outfit


class DisplayFamiliarParser(DisplayImageParser):
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
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None
        familiar = DisplayFamiliar(image_url=img_tag["src"], name=description, familiar_id=0)
        name = familiar.name.split("(")[0].strip()
        familiar.name = name
        m = id_regex.search(familiar.image_url)
        if m:
            familiar.familiar_id = int(m.group(1))
        return familiar


class AuctionParser:

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
        auction_row = parsed_content.select_one("div.Auction")
        if not auction_row:
            if "internal error" in content:
                return None
            raise InvalidContent("content does not belong to a auction details page in Tibia.com")
        auction = cls._parse_auction(auction_row)
        builder = AuctionDetailsBuilder()
        if skip_details:
            return auction

        details_tables = cls._parse_tables(parsed_content)
        if "General" in details_tables:
            cls._parse_general_table(builder, details_tables["General"])
        if "ItemSummary" in details_tables:
            builder.items(ItemSummaryParser._parse_table(details_tables["ItemSummary"]))
        if "StoreItemSummary" in details_tables:
            builder.store_items(ItemSummaryParser._parse_table(details_tables["StoreItemSummary"]))
        if "Mounts" in details_tables:
            builder.mounts(MountsParser._parse_table(details_tables["Mounts"]))
        if "StoreMounts" in details_tables:
            builder.store_mounts(MountsParser._parse_table(details_tables["StoreMounts"]))
        if "Outfits" in details_tables:
            builder.outfits(OutfitsParser._parse_table(details_tables["Outfits"]))
        if "StoreOutfits" in details_tables:
            builder.store_outfits(OutfitsParser._parse_table(details_tables["StoreOutfits"]))
        if "Familiars" in details_tables:
            builder.familiars(FamiliarsParser._parse_table(details_tables["Familiars"]))
        if "Blessings" in details_tables:
            cls._parse_blessings_table(builder, details_tables["Blessings"])
        if "Imbuements" in details_tables:
            builder.imbuements(cls._parse_single_column_table(details_tables["Imbuements"]))
        if "Charms" in details_tables:
            cls._parse_charms_table(builder, details_tables["Charms"])
        if "CompletedCyclopediaMapAreas" in details_tables:
            builder.completed_cyclopedia_map_areas(cls._parse_single_column_table(
                details_tables["CompletedCyclopediaMapAreas"]))
        if "CompletedQuestLines" in details_tables:
            builder.completed_quest_lines(cls._parse_single_column_table(details_tables["CompletedQuestLines"]))
        if "Titles" in details_tables:
            builder.titles(cls._parse_single_column_table(details_tables["Titles"]))
        if "Achievements" in details_tables:
            cls._parse_achievements_table(builder, details_tables["Achievements"])
        if "BestiaryProgress" in details_tables:
            cls._parse_bestiary_table(builder, details_tables["BestiaryProgress"])
        if "BosstiaryProgress" in details_tables:
            cls._parse_bestiary_table(builder, details_tables["BosstiaryProgress"], True)
        auction.details = builder.build()
        return auction


    @classmethod
    def _parse_auction(cls, auction_row, auction_id=0) -> Auction:
        """Parse an auction's table, extracting its data.

        Parameters
        ----------
        auction_row: :class:`bs4.Tag`
            The row containing the auction's information.
        auction_id: :class:`int`
            The ID of the auction.

        Returns
        -------
        :class:`Auction`
            The auction contained in the table.
        """
        header_container = auction_row.select_one("div.AuctionHeader")
        char_name_container = header_container.select_one("div.AuctionCharacterName")
        char_link = char_name_container.select_one("a")
        if char_link:
            url = urllib.parse.urlparse(char_link["href"])
            query = urllib.parse.parse_qs(url.query)
            auction_id = int(query["auctionid"][0])
            name = char_link.text
        else:
            name = char_name_container.text

        builder = AuctionBuilder().name(name).auction_id(auction_id)
        char_name_container.replaceWith('')
        m = char_info_regex.search(header_container.text)
        if m:
            builder.level(int(m.group(1)))
            builder.vocation(try_enum(Vocation, m.group(2).strip()))
            builder.sex(try_enum(Sex, m.group(3).strip().lower()))
            builder.world(m.group(4))
        outfit_img = auction_row.select_one("img.AuctionOutfitImage")
        m = id_addon_regex.search(outfit_img["src"])
        if m:
            builder.outfit(OutfitImage(image_url=outfit_img["src"], outfit_id=int(m.group(1)), addons=int(m.group(2))))
        item_boxes = auction_row.select("div.CVIcon")
        for item_box in item_boxes:
            item = DisplayItemParser._parse_image_box(item_box)
            if item:
                builder.add_displayed_item(item)
        dates_containers = auction_row.select_one("div.ShortAuctionData")
        start_date_tag, end_date_tag, *_ = dates_containers.select("div.ShortAuctionDataValue")
        builder.auction_start(parse_tibia_datetime(start_date_tag.text.replace('\xa0', ' ')))
        builder.auction_end(parse_tibia_datetime(end_date_tag.text.replace('\xa0', ' ')))
        bids_container = auction_row.select_one("div.ShortAuctionDataBidRow")
        bid_tag = bids_container.select_one("div.ShortAuctionDataValue")
        bid_type_tag = bids_container.select("div.ShortAuctionDataLabel")[0]
        bid_type_str = bid_type_tag.text.replace(":", "").strip()
        builder.bid_type(try_enum(BidType, bid_type_str))
        builder.bid(parse_integer(bid_tag.text))
        auction_body_block = auction_row.select_one("div.CurrentBid")
        auction_info_tag = auction_body_block.select_one("div.AuctionInfo")
        status = ""
        if auction_info_tag:
            convert_line_breaks(auction_info_tag)
            status = auction_info_tag.text.replace("\n", " ").replace("  ", " ")
        builder.status(try_enum(AuctionStatus, status, AuctionStatus.IN_PROGRESS))
        argument_entries = auction_row.select("div.Entry")
        for entry in argument_entries:
            img = entry.select_one("img")
            img_url = img["src"]
            category_id = 0
            m = id_regex.search(img_url)
            if m:
                category_id = parse_integer(m.group(1))
            builder.add_sales_argument(SalesArgument(content=entry.text, category_image=img_url,
                                                     category_id=category_id))
        return builder.build()

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
        details_tables = parsed_content.select("div.CharacterDetailsBlock")
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
        rows = table.select("tr")
        data = {}
        for row in rows:
            name = row.select_one("span").text
            value = row.select_one("div").text
            name = name.lower().strip().replace(" ", "_").replace(":", "")
            data[name] = value
        return data

    @classmethod
    def _parse_skills_table(cls, builder, table):
        """Parse the skills table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character's skill.
        """
        rows = table.select("tr")
        skills = []
        for row in rows:
            cols = row.select("td")
            name_c, level_c, progress_c = [c.text for c in cols]
            level = int(level_c)
            progress = float(progress_c.replace("%", ""))
            skills.append(SkillEntry(name=name_c, level=level, progress=progress))
        builder.skills(skills)

    @classmethod
    def _parse_blessings_table(cls, builder, table):
        """Parse the blessings table.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the character's blessings.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = table_content.select("tr")
        blessings = []
        for row in rows:
            cols = row.select("td")
            amount_c, name_c = [c.text for c in cols]
            amount = int(amount_c.replace("x", ""))
            blessings.append(BlessingEntry(name=name_c, amount=amount))
        builder.blessings(blessings)

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
        table_content = table.select("table.TableContent")[-1]
        _, *rows = table_content.select("tr")
        ret = []
        for row in rows:
            col = row.select_one("td")
            text = col.text
            if "more entries" in text:
                continue
            ret.append(text)
        return ret

    @classmethod
    def _parse_charms_table(cls, builder, table):
        """Parse the charms table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the charms.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = table_content.select("tr")
        charms = []
        for row in rows:
            cols = row.select("td")
            if len(cols) != 2:
                continue
            cost_c, name_c = [c.text for c in cols]
            cost = parse_integer(cost_c.replace("x", ""))
            charms.append(CharmEntry(name=name_c, cost=cost))
        builder.charms(charms)

    @classmethod
    def _parse_achievements_table(cls, builder, table):
        """Parse the achievements table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the achievements.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = table_content.select("tr")
        achievements = []
        for row in rows:
            col = row.select_one("td")
            text = col.text.strip()
            if "more entries" in text:
                continue
            secret = col.select_one("img") is not None
            achievements.append(AchievementEntry(name=text, secret=secret))
        builder.achievements(achievements)

    @classmethod
    def _parse_bestiary_table(cls, builder, table, bosstiary=False):
        """Parse the bestiary table and extracts its information.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table containing the bestiary information.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = table_content.select("tr")
        bestiary = []
        for row in rows:
            cols = row.select("td")
            if len(cols) != 3:
                continue
            step_c, kills_c, name_c = [c.text for c in cols]
            kills = parse_integer(kills_c.replace("x", ""))
            step = int(step_c)
            bestiary.append(BestiaryEntry(name=name_c, kills=kills, step=step))
        if bosstiary:
            builder.bosstiary_progress(bestiary)
        else:
            builder.bestiary_progress(bestiary)

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
        item_boxes = parsed_content.select("div.CVIcon")
        entries = []
        for item_box in item_boxes:
            item = entry_class._parse_image_box(item_box)
            if item:
                entries.append(item)
        return entries

    @classmethod
    def _parse_general_table(cls, builder, table):
        """Parse the general information table and assigns its values.

        Parameters
        ----------
        table: :class:`bs4.Tag`
            The table with general information.
        """
        content_containers = table.select("table.TableContent")
        general_stats = cls._parse_data_table(content_containers[0])
        builder.hit_points(parse_integer(general_stats.get("hit_points", "0")))
        builder.mana(parse_integer(general_stats.get("mana", "0")))
        builder.capacity(parse_integer(general_stats.get("capacity", "0")))
        builder.speed(parse_integer(general_stats.get("speed", "0")))
        builder.mounts_count(parse_integer(general_stats.get("mounts", "0")))
        builder.outfits_count(parse_integer(general_stats.get("outfits", "0")))
        builder.titles_count(parse_integer(general_stats.get("titles", "0")))
        builder.blessings_count(parse_integer(re.sub(r"/d+", "", general_stats.get("blessings", "0"))))

        cls._parse_skills_table(builder, content_containers[1])

        additional_stats = cls._parse_data_table(content_containers[2])
        builder.creation_date(parse_tibia_datetime(additional_stats.get("creation_date", "").replace("\xa0", " ")))
        builder.experience(parse_integer(additional_stats.get("experience", "0")))
        builder.gold(parse_integer(additional_stats.get("gold", "0")))
        builder.achievement_points(parse_integer(additional_stats.get("achievement_points", "0")))

        transfer_data = cls._parse_data_table(content_containers[3])
        transfer_text = transfer_data.get("regular_world_transfer")
        if "after" in transfer_text:
            date_string = transfer_text.split("after ")[1]
            builder.regular_world_transfer_available_date(parse_tibia_datetime(date_string))

        charms_data = cls._parse_data_table(content_containers[4])
        builder.charm_expansion("yes" in charms_data.get("charm_expansion", ""))
        builder.available_charm_points(parse_integer(charms_data.get("available_charm_points")))
        builder.spent_charm_points(parse_integer(charms_data.get("spent_charm_points")))

        daily_rewards_data = cls._parse_data_table(content_containers[5])
        builder.daily_reward_streak(parse_integer(daily_rewards_data.popitem()[1]))

        hunting_data = cls._parse_data_table(content_containers[6])
        builder.hunting_task_points(parse_integer(hunting_data.get("hunting_task_points", "")))
        builder.permanent_hunting_task_slots(parse_integer(hunting_data.get("permanent_hunting_task_slots", "")))
        builder.permanent_prey_slots(parse_integer(hunting_data.get("permanent_prey_slots", "")))
        builder.prey_wildcards(parse_integer(hunting_data.get("prey_wildcards", "")))

        hirelings_data = cls._parse_data_table(content_containers[7])
        builder.hirelings(parse_integer(hirelings_data.get("hirelings", "")))
        builder.hireling_jobs(parse_integer(hirelings_data.get("hireling_jobs", "")))
        builder.hireling_outfits(parse_integer(hirelings_data.get("hireling_outfits", "")))
        if len(content_containers) >= 9:
            dust_data = cls._parse_data_table(content_containers[8])
            dust_values = dust_data.get("exalted_dust", "0/0").split("/")
            builder.exalted_dust(parse_integer(dust_values[0]))
            builder.exalted_dust_limit(parse_integer(dust_values[1]))
        if len(content_containers) >= 10:
            boss_data = cls._parse_data_table(content_containers[9])
            builder.boss_points(parse_integer(boss_data.get("boss_points", "")))


class PaginatedSummaryParser:


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
        pagination_block = parsed_content.select_one("div.BlockPageNavigationRow")
        if pagination_block is not None:
            self.page, self.total_pages, self.results = parse_pagination(pagination_block)
    # endregion


class ItemSummaryParser(PaginatedSummary):
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
        page, total_pages, results = parse_pagination(table.select_one("div.BlockPageNavigationRow"))
        summary = ItemSummary(page=page, total_pages=total_pages, results=results)
        item_boxes = table.select("div.CVIcon")
        for item_box in item_boxes:
            item = DisplayItemParser._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class MountsParser(PaginatedSummary):
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
        page, total_pages, results = parse_pagination(table.select_one("div.BlockPageNavigationRow"))
        summary = Mounts(page=page, total_pages=total_pages, results=results)
        item_boxes = table.select("div.CVIcon")
        for item_box in item_boxes:
            item = DisplayMountParser._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class FamiliarsParser(PaginatedSummary):
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
        page, total_pages, results = parse_pagination(table.select_one("div.BlockPageNavigationRow"))
        summary = Familiars(page=page, total_pages=total_pages, results=results)
        item_boxes = table.select("div.CVIcon")
        for item_box in item_boxes:
            item = DisplayFamiliarParser._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary


class OutfitsParser:
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
        page, total_pages, results = parse_pagination(table.select_one("div.BlockPageNavigationRow"))
        summary = Outfits(page=page, total_pages=total_pages, results=results)
        item_boxes = table.select("div.CVIcon")
        for item_box in item_boxes:
            item = DisplayOutfitParser._parse_image_box(item_box)
            if item:
                summary.entries.append(item)
        return summary

