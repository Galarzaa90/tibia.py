import datetime
import logging
from contextlib import asynccontextmanager
from typing import Optional, Set, List

from fastapi import FastAPI, Path, Query

import tibiapy
from tibiapy import SpellVocationFilter, SpellGroup, SpellType, SpellSorting, NewsType, NewsCategory, \
    HouseStatus, HouseOrder, HouseType, HighscoresCategory, HighscoresProfession, HighscoresBattlEyeType, \
    PvpTypeFilter
from tibiapy.models import World, WorldOverview, Spell, SpellsSection, Highscores, TibiaResponse, EventSchedule, \
    CreatureEntry, BossEntry, CreaturesSection, Creature, BoostableBosses, Character, Guild, GuildWars, GuildsSection, \
    House, HousesSection, KillStatistics, Leaderboard, ForumSection, ForumBoard, ForumThread, CharacterBazaar, Auction
from tibiapy.models.news import News, NewsArchive

logging_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_formatter)
log = logging.getLogger("tibiapy")
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = tibiapy.Client()
    yield
    await app.state.client.session.close()


app = FastAPI(
    title="Tibia.py API",
    version=tibiapy.__version__,
    lifespan=lifespan,
)


@app.get("/healthcheck", tags=["General"])
async def healthcheck():
    return True


# region News

TYPES_DESCRIPTION = "The types of news to display. Leave empty to show any."
CATEGORIES_DESCRIPTION = "The categories of news to display. Leave empty to show any."


@app.get("/news/{fromDate}", tags=["News"],
         summary="Get news archive from date")
async def get_news_archive(
        from_date: datetime.date = Path(..., alias="fromDate"),
        types: Set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: Set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    """Show the news archive from a start date to today."""
    return await app.state.client.fetch_news_archive(from_date, None, categories, types)


@app.get("/news/{fromDate}/{toDate}", tags=["News"],
         summary="Get news archive between dates")
async def get_news_archive(
        from_date: datetime.date = Path(..., alias="fromDate"),
        to_date: datetime.date = Path(..., alias="toDate"),
        types: Set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: Set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    """Show the news archive for a specific date period."""
    return await app.state.client.fetch_news_archive(from_date, to_date, categories, types)


@app.get("/news", tags=["News"])
async def get_news_archive_by_days(
        days: int = Query(30),
        types: Set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: Set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    return await app.state.client.fetch_news_archive_by_days(days, categories, types)


@app.get("/news/{news_id}", tags=["News"])
async def get_news_article(
        news_id: int = Path(...)
) -> TibiaResponse[Optional[News]]:
    return await app.state.client.fetch_news(news_id=news_id)


@app.get("/events/", tags=["News"])
async def get_current_events_schedule() -> TibiaResponse[EventSchedule]:
    """Get the event calendar for the current month."""
    return await app.state.client.fetch_event_schedule()


@app.get("/events/{year}/{month}", tags=["News"])
async def get_events_schedule(
        year: int = Path(...),
        month: int = Path(...),
) -> TibiaResponse[EventSchedule]:
    """Get the event calendar for a specific year and month."""
    return await app.state.client.fetch_event_schedule(month, year)


# endregion

# region Library

@app.get("/creatures/boosted", tags=["Library"])
async def get_boosted_creature() -> TibiaResponse[CreatureEntry]:
    return await app.state.client.fetch_boosted_creature()


@app.get("/bosses/boosted", tags=["Library"])
async def get_boosted_boss() -> TibiaResponse[BossEntry]:
    return await app.state.client.fetch_boosted_boss()


@app.get("/library/creatures", tags=["Library"])
async def get_creatures() -> TibiaResponse[CreaturesSection]:
    return await app.state.client.fetch_creatures()


@app.get("/library/creatures/{identifier}", tags=["Library"])
async def get_creature(identifier: str = Path(...)) -> TibiaResponse[Optional[Creature]]:
    return await app.state.client.fetch_creature(identifier)


@app.get("/library/bosses", tags=["Library"])
async def get_bosses() -> TibiaResponse[BoostableBosses]:
    return await app.state.client.fetch_boostable_bosses()


@app.get("/library/spells", tags=["Library"])
async def get_spells(
        vocation: SpellVocationFilter = Query(None),
        group: SpellGroup = Query(None),
        type: SpellType = Query(None),
        premium: bool = Query(None),
        sort: SpellSorting = Query(None),
) -> TibiaResponse[SpellsSection]:
    return await app.state.client.fetch_spells(vocation=vocation, group=group, spell_type=type, premium=premium,
                                               sort=sort)


@app.get("/library/spells/{identifier}", tags=["Library"])
async def get_spell(
        identifier: str = Path(...)
) -> TibiaResponse[Optional[Spell]]:
    return await app.state.client.fetch_spell(identifier)


# endregion

# region Community


@app.get("/characters/{name}", tags=["Community"])
async def get_character(
        name: str = Path(...)
) -> TibiaResponse[Optional[Character]]:
    return await app.state.client.fetch_character(name)


@app.get("/worlds", tags=["Community"])
async def get_worlds() -> TibiaResponse[WorldOverview]:
    return await app.state.client.fetch_world_overview()


@app.get("/worlds/{name}", tags=["Community"])
async def get_world(name: str = Path(...)) -> TibiaResponse[Optional[World]]:
    return await app.state.client.fetch_world(name)


@app.get("/guilds/{name}", tags=["Community"])
async def get_guild(
        name: str = Path(...)
) -> TibiaResponse[Optional[Guild]]:
    return await app.state.client.fetch_guild(name)


@app.get("/guilds/{name}/wars", tags=["Community"])
async def get_guild_wars(
        name: str = Path(...)
) -> TibiaResponse[Optional[GuildWars]]:
    return await app.state.client.fetch_guild_wars(name)


@app.get("/worlds/{world}/guilds", tags=["Community"])
async def get_world_guilds(
        world: str = Path(...)
) -> TibiaResponse[Optional[GuildsSection]]:
    return await app.state.client.fetch_world_guilds(world)


@app.get("/highscores/{world}", tags=["Community"])
async def get_highscores(
        world: str = Path(...),
        page: int = Query(1),
        category: HighscoresCategory = Query(HighscoresCategory.EXPERIENCE),
        vocation: HighscoresProfession = Query(HighscoresProfession.ALL),
        battleye: HighscoresBattlEyeType = Query(None),
        pvp_types: List[PvpTypeFilter] = Query([], alias="pvp"),
) -> TibiaResponse[Highscores]:
    if world.lower() in ("global", "all"):
        world = None
    return await app.state.client.fetch_highscores_page(world, category, page=page, vocation=vocation,
                                                        battleye_type=battleye,
                                                        pvp_types=pvp_types)


@app.get("/houses/{world}/{house_id:int}", tags=["Community"])
async def get_house(
        world: str = Path(...),
        house_id: int = Path(...)
) -> TibiaResponse[Optional[House]]:
    return await app.state.client.fetch_house(house_id, world)


@app.get("/houses/{world}/{town}", tags=["Community"])
async def get_houses_section(
        world: str = Path(...),
        town: str = Path(...),
        status: HouseStatus = Query(None),
        order: HouseOrder = Query(None),
        house_type: HouseType = Query(None, alias="type"),
) -> TibiaResponse[Optional[HousesSection]]:
    return await app.state.client.fetch_houses_section(world, town, status=status, order=order, house_type=house_type)


@app.get("/killStatistics/{world}", tags=["Community"])
@app.get("/killstatistics/{world}", tags=["Community"])
async def get_kill_statistics(
        world: str = Path(...)
) -> TibiaResponse[Optional[KillStatistics]]:
    return await app.state.client.fetch_kill_statistics(world)


@app.get("/leaderboards/{world}", tags=["Community"])
async def get_leaderboards(
        world: str = Path(...)
) -> TibiaResponse[Optional[Leaderboard]]:
    return await app.state.client.fetch_leaderboard(world=world)


# endregion

# region Forums

@app.get("/forums/world", tags=["Forums"])
async def get_world_boards() -> TibiaResponse[ForumSection]:
    return await app.state.client.fetch_forum_world_boards()


@app.get("/forums/trade", tags=["Forums"])
async def get_trade_boards() -> TibiaResponse[ForumSection]:
    return await app.state.client.fetch_forum_trade_boards()


@app.get("/forums/community", tags=["Forums"])
async def get_community_boards() -> TibiaResponse[ForumSection]:
    return await app.state.client.fetch_forum_community_boards()


@app.get("/forums/support", tags=["Forums"])
async def get_support_boards() -> TibiaResponse[ForumSection]:
    return await app.state.client.fetch_forum_support_boards()


@app.get("/forums/sections/{section_id}", tags=["Forums"])
async def get_forum_section(
        section_id: int = Path(...)
) -> TibiaResponse[Optional[ForumSection]]:
    return await app.state.client.fetch_forum_section(section_id)


@app.get("/forums/boards/{board_id}", tags=["Forums"])
async def get_forum_board(
        board_id: int = Path(...),
        page: int = Query(1),
        age: int = Query(30),
) -> TibiaResponse[Optional[ForumBoard]]:
    return await app.state.client.fetch_forum_board(board_id=board_id, page=page, age=age)


@app.get("/forums/threads/{thread_id}", tags=["Forums"])
async def get_forum_thread(
        thread_id: int = Path(...),
        page: int = Query(1),
) -> TibiaResponse[Optional[ForumThread]]:
    return await app.state.client.fetch_forum_thread(thread_id=thread_id, page=page)


# endregion

# region Char Bazaar

@app.get("/auctions", tags=["Char Bazaar"])
async def get_current_auctions(
        page: int = Query(1)
) -> TibiaResponse[CharacterBazaar]:
    return await app.state.client.fetch_current_auctions(page)


@app.get("/auctions/{auction_id}", tags=["Char Bazaar"])
async def get_auction(
        auction_id: int = Path(...),
        skip_details: bool = Query(False),
        fetch_items: bool = Query(False),
        fetch_mounts: bool = Query(False),
        fetch_outfits: bool = Query(False),
        fetch_familiars: bool = Query(False),
) -> TibiaResponse[Optional[Auction]]:
    return await app.state.client.fetch_auction(auction_id, skip_details=skip_details, fetch_items=fetch_items,
                                                fetch_mounts=fetch_mounts, fetch_outfits=fetch_outfits,
                                                fetch_familiars=fetch_familiars)

# endregion
