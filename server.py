import datetime
import logging
from contextlib import asynccontextmanager
from typing import Optional, Set, List

from fastapi import FastAPI, Path, Query

import tibiapy
from tibiapy import SpellVocationFilter, SpellGroup, SpellType, SpellSorting, TibiaResponse, NewsType, NewsCategory, \
    HouseStatus, HouseOrder, HouseType, HighscoresCategory, HighscoresProfession, HighscoresBattlEyeType, \
    AuctionPvpTypeFilter
from tibiapy.models import World, WorldOverview, Spell, SpellsSection, Highscores
from tibiapy.models.news import News

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


app = FastAPI(lifespan=lifespan)


@app.get("/news/{start_date}/{end_date}")
async def get_news_archive(
        start_date: datetime.date = Path(...),
        end_date: datetime.date = Path(...),
        types: Set[NewsType] = Query(None, alias="type"),
        categories: Set[NewsCategory] = Query(None, alias="category"),
):
    return await app.state.client.fetch_news_archive(start_date, end_date, categories, types)


# region News

@app.get("/news")
async def get_news_archive_by_days(
        days: int = Query(30),
        types: Set[NewsType] = Query(None, alias="type"),
        categories: Set[NewsCategory] = Query(None, alias="category"),
):
    return await app.state.client.fetch_news_archive_by_days(days, categories, types)


@app.get("/news/{news_id}")
async def get_news_article(
        news_id: int = Path(...)
) -> TibiaResponse[Optional[News]]:
    return await app.state.client.fetch_news(news_id=news_id)


@app.get("/events/{year}/{month}")
async def get_events_schedule(
        year: int = Path(...),
        month: int = Path(...),
):
    return await app.state.client.fetch_event_schedule(month, year)


# endregion

# region Library

@app.get("/library/creatures")
async def get_creatures():
    return await app.state.client.fetch_creatures()


@app.get("/library/creatures/{identifier}")
async def get_creature(identifier: str = Path(...)):
    return await app.state.client.fetch_creature(identifier)


@app.get("/library/bosses")
async def get_bosses():
    return await app.state.client.fetch_boostable_bosses()


@app.get("/library/spells")
async def get_spells(
        vocation: SpellVocationFilter = Query(None),
        group: SpellGroup = Query(None),
        type: SpellType = Query(None),
        premium: bool = Query(None),
        sort: SpellSorting = Query(None),
) -> TibiaResponse[SpellsSection]:
    return await app.state.client.fetch_spells(vocation=vocation, group=group, spell_type=type, premium=premium,
                                               sort=sort)


@app.get("/library/spells/{identifier}")
async def get_spell(
        identifier: str = Path(...)
) -> TibiaResponse[Optional[Spell]]:
    return await app.state.client.fetch_spell(identifier)


# endregion

# region Community


@app.get("/characters/{name}")
async def get_character(
        name: str = Path(...)
):
    return await app.state.client.fetch_character(name)


@app.get("/worlds")
async def get_worlds() -> TibiaResponse[WorldOverview]:
    return await app.state.client.fetch_world_overview()


@app.get("/worlds/{name}")
async def get_world(name: str = Path(...)) -> TibiaResponse[Optional[World]]:
    return await app.state.client.fetch_world(name)


# endregion

@app.get("/cmposts/{start_date}/{end_date}")
async def get_cm_posts_archive(
        start_date: datetime.date = Path(...),
        end_date: datetime.date = Path(...),
):
    return await app.state.client.fetch_cm_post_archive(start_date, end_date)


@app.get("/auctions")
async def get_current_auctions(
        page: int = Query(1)
):
    return await app.state.client.fetch_current_auctions(page)


@app.get("/auctions/{auction_id}")
async def get_auction(
        auction_id: int = Path(...),
        skip_details: bool = Query(False),
        fetch_items: bool = Query(False),
        fetch_mounts: bool = Query(False),
        fetch_outfits: bool = Query(False),
        fetch_familiars: bool = Query(False),
):
    return await app.state.client.fetch_auction(auction_id, skip_details=skip_details, fetch_items=fetch_items,
                                                fetch_mounts=fetch_mounts, fetch_outfits=fetch_outfits,
                                                fetch_familiars=fetch_familiars)



@app.get("/creatures/boosted")
async def get_boosted_creature():
    return await app.state.client.fetch_boosted_creature()


@app.get("/bosses/boosted")
async def get_boosted_creature():
    return await app.state.client.fetch_boosted_boss()


@app.get("/forums/world")
async def get_world_boards():
    return await app.state.client.fetch_forum_world_boards()


@app.get("/forums/trade")
async def get_trade_boards():
    return await app.state.client.fetch_forum_trade_boards()


@app.get("/forums/community")
async def get_community_boards():
    return await app.state.client.fetch_forum_community_boards()


@app.get("/forums/support")
async def get_support_boards():
    return await app.state.client.fetch_forum_support_boards()


@app.get("/forums/sections/{section_id}")
async def get_forum_section(
        section_id: int = Path(...)
):
    return await app.state.client.fetch_forum_section(section_id)


@app.get("/forums/boards/{board_id}")
async def get_forum_board(
        board_id: int = Path(...),
        page: int = Query(1),
        age: int = Query(30),
):
    return await app.state.client.fetch_forum_board(board_id=board_id, page=page, age=age)


@app.get("/forums/threads/{thread_id}")
async def get_forum_board(
        thread_id: int = Path(...),
        page: int = Query(1),
):
    return await app.state.client.fetch_forum_thread(thread_id=thread_id, page=page)


@app.get("/guilds/{name}")
async def get_guild(
        name: str = Path(...)
):
    return await app.state.client.fetch_guild(name)


@app.get("/guilds/{name}/wars")
async def get_guild_wars(
        name: str = Path(...)
):
    return await app.state.client.fetch_guild_wars(name)


@app.get("/worlds/{world}/guilds")
async def get_world_guilds(
        world: str = Path(...)
):
    return await app.state.client.fetch_world_guilds(world)


@app.get("/highscores/{world}")
async def get_highscores(
        world: str = Path(...),
        page: int = Query(1),
        category: HighscoresCategory = Query(HighscoresCategory.EXPERIENCE),
        vocation: HighscoresProfession = Query(HighscoresProfession.ALL),
        battleye: HighscoresBattlEyeType = Query(None),
        pvp_types: List[AuctionPvpTypeFilter] = Query([], alias="pvp"),
) -> TibiaResponse[Highscores]:
    if world.lower() in ("global", "all"):
        world = None
    return await app.state.client.fetch_highscores_page(world, category, page=page, vocation=vocation,
                                                        battleye_type=battleye,
                                                        pvp_types=pvp_types)


@app.get("/houses/{world}/{house_id}")
async def get_house(
        world: str = Path(...),
        house_id: int = Path(...)
):
    return await app.state.client.fetch_house(house_id, world)


@app.get("/houses/{world}/{town}")
async def get_houses_section(
        world: str = Path(...),
        town: str = Path(...),
        status: HouseStatus = Query(None),
        order: HouseOrder = Query(None),
        house_type: HouseType = Query(None, alias="type"),
):
    return await app.state.client.fetch_world_houses(world, town, status=status, order=order, house_type=house_type)


@app.get("/killStatistics/{world}")
@app.get("/killstatistics/{world}")
async def get_kill_statistics(
        world: str = Path(...)
):
    return await app.state.client.fetch_kill_statistics(world)


@app.get("/leaderboards/{world}")
async def get_leaderboards(
        world: str = Path(...)
):
    return await app.state.client.fetch_leaderboard(world=world)




