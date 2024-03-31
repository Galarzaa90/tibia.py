"""Contains all classes related to the Character Bazaar sections in Tibia.com."""
import logging
import re
import urllib.parse
from typing import Dict, List, Optional

import bs4

from tibiapy import InvalidContentError
from tibiapy.builders import AuctionBuilder, AuctionDetailsBuilder, CharacterBazaarBuilder
from tibiapy.enums import AuctionBattlEyeFilter, AuctionOrderBy, AuctionOrderDirection, AuctionSearchType, \
    AuctionSkillFilter, AuctionStatus, AuctionVocationFilter, BazaarType, BidType, PvpTypeFilter, Sex, Vocation
from tibiapy.models import (AchievementEntry, AjaxPaginator, Auction, AuctionFilters, BestiaryEntry, BlessingEntry,
                            CharacterBazaar, CharmEntry, FamiliarEntry, Familiars, ItemEntry, ItemSummary, MountEntry,
                            Mounts, OutfitEntry, OutfitImage, Outfits, SalesArgument, SkillEntry)
from tibiapy.models.bazaar import DisplayImage, RevealedGem
from tibiapy.utils import (clean_text, convert_line_breaks, get_rows, parse_form_data, parse_integer, parse_pagination,
                           parse_tibia_datetime, parse_tibiacom_content, try_enum)

CSS_CLASS_ICON = "div.CVIcon"

results_pattern = re.compile(r"Results: (\d+)")
char_info_regex = re.compile(r"Level: (\d+) \| Vocation: ([\w\s]+)\| (\w+) \| World: (\w+)")
id_addon_regex = re.compile(r"(\d{1,4})_(\d)\.gif$")
id_regex = re.compile(r"(\d{1,5}).(?:gif|png)$")
description_regex = re.compile(r'"(?:an?\s)?([^"]+)"')
amount_regex = re.compile(r"([\d,]{1,9})x")
tier_regex = re.compile(r"(.*)\s\(tier (\d)\)")

log = logging.getLogger("tibiapy")

__all__ = (
    "CharacterBazaarParser",
    "AuctionParser",
)


class AuctionFiltersParser:
    @classmethod
    def parse_from_table(cls, table: bs4.Tag) -> AuctionFilters:
        """Parse the filters table to extract its values.

        Parameters
        ----------
        table:
            The table containing the filters.

        Returns
        -------
        :class:`.AuctionFilters`
            The currently applied filters.
        """
        filters = AuctionFilters()
        forms = table.select("form")
        data = parse_form_data(forms[0])

        filters.world = data.values["filter_world"]
        filters.available_worlds = [w for w in data.available_options["filter_world"] if "(" not in w]
        filters.pvp_type = try_enum(PvpTypeFilter, parse_integer(data.values.get("filter_worldpvptype"), None))
        filters.battleye = try_enum(AuctionBattlEyeFilter,
                                    parse_integer(data.values.get("filter_worldbattleyestate"), None))
        filters.vocation = try_enum(AuctionVocationFilter, parse_integer(data.values.get("filter_profession"), None))
        filters.min_level = parse_integer(data.values.get("filter_levelrangefrom"), None)
        filters.max_level = parse_integer(data.values.get("filter_levelrangeto"), None)
        filters.skill = try_enum(AuctionSkillFilter, parse_integer(data.values.get("filter_skillid"), None))
        filters.min_skill_level = parse_integer(data.values.get("filter_skillrangefrom"), None)
        filters.max_skill_level = parse_integer(data.values.get("filter_skillrangeto"), None)
        filters.order_by = try_enum(AuctionOrderBy, parse_integer(data.values.get("order_column"), None))
        filters.order = try_enum(AuctionOrderDirection, parse_integer(data.values.get("order_direction"), None))
        if len(forms) > 1:
            data_search = parse_form_data(forms[1])
            filters.search_string = data_search.values.get("searchstring")
            filters.search_type = try_enum(AuctionSearchType, parse_integer(data_search.values.get("searchtype"), None))

        return filters


class CharacterBazaarParser:
    """Parser for the character bazaar in Tibia.com."""

    @classmethod
    def from_content(cls, content: str) -> CharacterBazaar:
        """Get the bazaar's information and list of auctions from Tibia.com.

        Parameters
        ----------
        content:
            The HTML content of the bazaar section at Tibia.com.

        Returns
        -------
            The character bazaar with the entries found.
        """
        try:
            parsed_content = parse_tibiacom_content(content, builder="html5lib")
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
                builder.filters(AuctionFiltersParser.parse_from_table(filter_table))

            if page_navigation_row := parsed_content.select_one("td.PageNavigation"):
                page, total_pages, results_count = parse_pagination(page_navigation_row)
                builder.current_page(page).total_pages(total_pages).results_count(results_count)

            auction_rows = auctions_table.select("div.Auction")
            for auction_row in auction_rows:
                auction = AuctionParser._parse_auction(auction_row)

                builder.add_entry(auction)

            return builder.build()
        except (ValueError, IndexError) as e:
            raise InvalidContentError("content does not belong to the bazaar at Tibia.com", original=e) from e


class AuctionParser:
    """Parser for Tibia.com character auctions."""

    @classmethod
    def from_content(cls, content: str, auction_id: int = 0, skip_details: bool = False) -> Optional[Auction]:
        """Parse an auction detail page from Tibia.com and extracts its data.

        Parameters
        ----------
        content:
            The HTML content of the auction detail page in Tibia.com
        auction_id:
            The ID of the auction.

            It is not possible to extract the ID from the page's content, so it may be passed to assign it manually.
        skip_details:
            Whether to skip parsing the entire auction and only parse the information shown in lists. False by default.

            This allows fetching basic information like name, level, vocation, world, bid and status, shaving off some
            parsing time.

        Returns
        -------
            The auction details if found, :obj:`None` otherwise.

        Raises
        ------
        InvalidContent
            If the content does not belong to an auction detail's page.
        """
        parsed_content = parse_tibiacom_content(content, builder="lxml" if skip_details else "html5lib")
        auction_row = parsed_content.select_one("div.Auction")
        if not auction_row:
            if "internal error" in content:
                return None

            raise InvalidContentError("content does not belong to a auction details page in Tibia.com")

        auction = cls._parse_auction(auction_row, auction_id)
        builder = AuctionDetailsBuilder()
        if skip_details:
            return auction

        details_tables = cls._parse_tables(parsed_content)
        if "General" in details_tables:
            cls._parse_general_table(builder, details_tables["General"])

        if "ItemSummary" in details_tables:
            builder.items(cls._parse_items_table(details_tables["ItemSummary"]))

        if "StoreItemSummary" in details_tables:
            builder.store_items(cls._parse_items_table(details_tables["StoreItemSummary"]))

        if "Mounts" in details_tables:
            builder.mounts(cls._parse_mounts_table(details_tables["Mounts"]))

        if "StoreMounts" in details_tables:
            builder.store_mounts(cls._parse_mounts_table(details_tables["StoreMounts"]))

        if "Outfits" in details_tables:
            builder.outfits(cls._parse_outfits_table(details_tables["Outfits"]))

        if "StoreOutfits" in details_tables:
            builder.store_outfits(cls._parse_outfits_table(details_tables["StoreOutfits"]))

        if "Familiars" in details_tables:
            builder.familiars(cls._parse_familiars_table(details_tables["Familiars"]))

        if "Blessings" in details_tables:
            cls._parse_blessings_table(builder, details_tables["Blessings"])

        if "Imbuements" in details_tables:
            builder.imbuements(cls._parse_single_column_table(details_tables["Imbuements"]))

        if "Charms" in details_tables:
            cls._parse_charms_table(builder, details_tables["Charms"])

        if "CompletedCyclopediaMapAreas" in details_tables:
            builder.completed_cyclopedia_map_areas(
                cls._parse_single_column_table(details_tables["CompletedCyclopediaMapAreas"]),
            )

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

        if "RevealedGems" in details_tables:
            cls._parse_revealed_gems_table(builder, details_tables["RevealedGems"])

        auction.details = builder.build()
        return auction

    @classmethod
    def _parse_auction(cls, auction_row: bs4.Tag, auction_id: int = 0) -> Auction:
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
        if char_link := char_name_container.select_one("a"):
            url = urllib.parse.urlparse(char_link["href"])
            query = urllib.parse.parse_qs(url.query)
            auction_id = int(query["auctionid"][0])
            name = char_link.text
        else:
            name = char_name_container.text

        builder = AuctionBuilder().name(name).auction_id(auction_id)
        char_name_container.replaceWith("")
        if m := char_info_regex.search(header_container.text):
            builder.level(int(m.group(1)))
            builder.vocation(try_enum(Vocation, m.group(2).strip()))
            builder.sex(try_enum(Sex, m.group(3).strip().lower()))
            builder.world(m.group(4))

        outfit_img = auction_row.select_one("img.AuctionOutfitImage")
        if m := id_addon_regex.search(outfit_img["src"]):
            builder.outfit(OutfitImage(image_url=outfit_img["src"], outfit_id=int(m.group(1)), addons=int(m.group(2))))

        item_boxes = auction_row.select(CSS_CLASS_ICON)
        for item_box in item_boxes:
            if item := cls._parse_displayed_item(item_box):
                builder.add_displayed_item(item)

        dates_containers = auction_row.select_one("div.ShortAuctionData")
        start_date_tag, end_date_tag, *_ = dates_containers.select("div.ShortAuctionDataValue")
        builder.auction_start(parse_tibia_datetime(clean_text(start_date_tag)))
        builder.auction_end(parse_tibia_datetime(clean_text(end_date_tag)))
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
            if m := id_regex.search(img_url):
                category_id = parse_integer(m.group(1))

            builder.add_sales_argument(SalesArgument(content=entry.text, category_image=img_url,
                                                     category_id=category_id))

        return builder.build()

    @classmethod
    def _parse_tables(cls, parsed_content: bs4.Tag) -> Dict[str, bs4.Tag]:
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
    def _parse_data_table(cls, table: bs4.Tag) -> Dict[str, str]:
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
        rows = get_rows(table)
        data = {}
        for row in rows:
            name = row.select_one("span").text
            value = row.select_one("div").text
            name = name.lower().strip().replace(" ", "_").replace(":", "")
            data[name] = value

        return data

    @classmethod
    def _parse_skills_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        """Parse the skills' table.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the character's skill.
        """
        rows = get_rows(table)
        skills = []
        for row in rows:
            cols = row.select("td")
            name_c, level_c, progress_c = (c.text for c in cols)
            level = int(level_c)
            progress = float(progress_c.replace("%", ""))
            skills.append(SkillEntry(name=name_c, level=level, progress=progress))

        builder.skills(skills)

    @classmethod
    def _parse_blessings_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        """Parse the blessings table.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the character's blessings.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = get_rows(table_content)
        blessings = []
        for row in rows:
            cols = row.select("td")
            amount_c, name_c = (c.text for c in cols)
            amount = int(amount_c.replace("x", ""))
            blessings.append(BlessingEntry(name=name_c, amount=amount))

        builder.blessings(blessings)

    @classmethod
    def _parse_single_column_table(cls, table: bs4.Tag) -> List[str]:
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
        _, *rows = get_rows(table_content)
        ret = []
        for row in rows:
            col = row.select_one("td")
            text = col.text
            if "more entries" in text:
                continue

            ret.append(text)

        return ret

    @classmethod
    def _parse_charms_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        """Parse the charms' table and extracts its information.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the charms.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = get_rows(table_content)
        charms = []
        for row in rows:
            cols = row.select("td")
            if len(cols) != 2:
                continue

            cost_c, name_c = (c.text for c in cols)
            cost = parse_integer(cost_c.replace("x", ""))
            charms.append(CharmEntry(name=name_c, cost=cost))

        builder.charms(charms)

    @classmethod
    def _parse_achievements_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        """Parse the achievements' table and extracts its information.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the achievements.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = get_rows(table_content)
        achievements = []
        for row in rows:
            col = row.select_one("td")
            text = col.text.strip()
            if "more entries" in text:
                continue

            secret = col.select_one("img") is not None
            achievements.append(AchievementEntry(name=text, is_secret=secret))

        builder.achievements(achievements)

    @classmethod
    def _parse_bestiary_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag, bosstiary: bool = False) -> None:
        """Parse the bestiary table and extracts its information.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
        table: :class:`bs4.Tag`
            The table containing the bestiary information.
        bosstiary: :class:`bool`
            Whether this is a bosstiary table or a bestiary table.
        """
        table_content = table.select_one("table.TableContent")
        _, *rows = get_rows(table_content)
        bestiary = []
        for row in rows:
            cols = row.select("td")
            if len(cols) != 3:
                continue

            step_c, kills_c, name_c = (c.text for c in cols)
            kills = parse_integer(kills_c.replace("x", ""))
            step = int(step_c)
            bestiary.append(BestiaryEntry(name=name_c, kills=kills, step=step))

        if bosstiary:
            builder.bosstiary_progress(bestiary)
        else:
            builder.bestiary_progress(bestiary)

    @classmethod
    def _parse_general_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        """Parse the general information table and assigns its values.

        Parameters
        ----------
        builder: :class:`AuctionDetailsBuilder`
            The builder where data will be stored to.
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
        builder.creation_date(parse_tibia_datetime(clean_text(additional_stats.get("creation_date", ""))))
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

        if len(content_containers) >= 11:
            bonus_promotion_data = cls._parse_data_table(content_containers[10])
            builder.bonus_promotion_points(parse_integer(bonus_promotion_data.get("bonus_promotion_points", "")))

    @classmethod
    def _parse_items_table(cls, table: bs4.Tag) -> ItemSummary:
        if pagination_block := table.select_one("div.BlockPageNavigationRow"):
            page, total_pages, results = parse_pagination(pagination_block)
        else:
            return ItemSummary()

        summary = ItemSummary(current_page=page, total_pages=total_pages, results_count=results)
        item_boxes = table.select(CSS_CLASS_ICON)
        for item_box in item_boxes:
            if item := cls._parse_displayed_item(item_box):
                summary.entries.append(item)

        return summary

    @classmethod
    def _parse_mounts_table(cls, table: bs4.Tag) -> Mounts:
        if pagination_block := table.select_one("div.BlockPageNavigationRow"):
            page, total_pages, results = parse_pagination(pagination_block)
        else:
            return Mounts()

        summary = Mounts(current_page=page, total_pages=total_pages, results_count=results)
        mount_boxes = table.select(CSS_CLASS_ICON)
        for mount_box in mount_boxes:
            if mount := cls._parse_displayed_mount(mount_box):
                summary.entries.append(mount)

        return summary

    @classmethod
    def _parse_outfits_table(cls, table: bs4.Tag) -> Outfits:
        if pagination_block := table.select_one("div.BlockPageNavigationRow"):
            page, total_pages, results = parse_pagination(pagination_block)
        else:
            return Outfits()

        summary = Outfits(current_page=page, total_pages=total_pages, results_count=results)
        outfit_boxes = table.select(CSS_CLASS_ICON)
        for outfit_box in outfit_boxes:
            if outfit := cls._parse_displayed_outfit(outfit_box):
                summary.entries.append(outfit)

        return summary

    @classmethod
    def _parse_familiars_table(cls, table: bs4.Tag) -> Familiars:
        if pagination_block := table.select_one("div.BlockPageNavigationRow"):
            page, total_pages, results = parse_pagination(pagination_block)
        else:
            return Familiars()

        summary = Familiars(current_page=page, total_pages=total_pages, results_count=results)
        familiar_boxes = table.select(CSS_CLASS_ICON)
        for familiar_box in familiar_boxes:
            if familiar := cls._parse_displayed_familiar(familiar_box):
                summary.entries.append(familiar)

        return summary

    @classmethod
    def _parse_displayed_item(cls, item_box: bs4.Tag) -> Optional[ItemEntry]:
        title_text = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None

        m = amount_regex.match(title_text)
        amount = 1
        if m:
            amount = parse_integer(m.group(1))
            title_text = amount_regex.sub("", title_text, 1).strip()

        name, *desc = title_text.split("\n")
        description = " ".join(desc) if desc else None
        tier = 0
        if m := tier_regex.search(name):
            tier = int(m.group(2))
            name = m.group(1)

        item_id = int(m.group(1)) if (m := id_regex.search(img_tag["src"])) else 0
        return ItemEntry(image_url=img_tag["src"], name=name, count=amount, item_id=item_id, description=description,
                         tier=tier)

    @classmethod
    def _parse_displayed_mount(cls, item_box: bs4.Tag) -> Optional[MountEntry]:
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None

        mount = MountEntry(image_url=img_tag["src"], name=description, mount_id=0)
        if m := id_regex.search(mount.image_url):
            mount.mount_id = int(m.group(1))

        return mount

    @classmethod
    def _parse_displayed_outfit(cls, item_box: bs4.Tag) -> Optional[OutfitEntry]:
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None

        outfit = OutfitEntry(image_url=img_tag["src"], name=description, outfit_id=0, addons=0)
        name = outfit.name.split("(")[0].strip()
        outfit.name = name
        if m := id_addon_regex.search(outfit.image_url):
            outfit.outfit_id = int(m.group(1))
            outfit.addons = int(m.group(2))

        return outfit

    @classmethod
    def _parse_displayed_familiar(cls, item_box: bs4.Tag) -> Optional[FamiliarEntry]:
        description = item_box["title"]
        img_tag = item_box.select_one("img")
        if not img_tag:
            return None

        familiar = FamiliarEntry(image_url=img_tag["src"], name=description, familiar_id=0)
        name = familiar.name.split("(")[0].strip()
        familiar.name = name
        if m := id_regex.search(familiar.image_url):
            familiar.familiar_id = int(m.group(1))

        return familiar

    @classmethod
    def _parse_revealed_gems_table(cls, builder: AuctionDetailsBuilder, table: bs4.Tag) -> None:
        table_content = table.select_one("table.TableContent")
        _, *rows = get_rows(table_content)
        for row in rows:
            gem_tag = row.select_one("div.Gem")
            gem_type = gem_tag["title"]
            effects = [t.text for t in row.select("span")]
            builder.add_revealed_gem(RevealedGem(
                gem_type=gem_type,
                mods=effects,
            ))

    @classmethod
    def _parse_page_items(cls, content: str, paginator: AjaxPaginator) -> List[DisplayImage]:
        parsed_content = parse_tibiacom_content(content, builder="html5lib")
        item_boxes = parsed_content.select(CSS_CLASS_ICON)
        entries = []
        for item_box in item_boxes:
            if isinstance(paginator, ItemSummary):
                item = cls._parse_displayed_item(item_box)
            elif isinstance(paginator, Outfits):
                item = cls._parse_displayed_outfit(item_box)
            elif isinstance(paginator, Mounts):
                item = cls._parse_displayed_mount(item_box)
            elif isinstance(paginator, Familiars):
                item = cls._parse_displayed_familiar(item_box)
            else:
                raise TypeError("unsupported paginator type")

            if item:
                entries.append(item)

        return entries
