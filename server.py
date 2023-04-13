import logging
from contextlib import asynccontextmanager
from typing import Optional, Set, List

from fastapi import FastAPI, Path, Query

import tibiapy
from tibiapy import VocationSpellFilter, SpellGroup, SpellType, SpellSorting, TibiaResponse, NewsType, NewsCategory, \
    HouseStatus, HouseOrder, HouseType, Category, VocationFilter, BattlEyeHighscoresFilter, PvpTypeFilter
from tibiapy.models import World, WorldOverview, Spell, SpellsSection, Highscores
from tibiapy.models.news import NewsArchive, News

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


@app.get("/forums/boards/{board_id}")
async def get_forum_board(
        board_id: int = Path(...),
        page: int = Query(1),
        age: int = Query(30),
):
    return await app.state.client.fetch_forum_board(board_id=board_id, page=page, age=age)


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
        category: Category = Query(Category.EXPERIENCE),
        vocation: VocationFilter = Query(VocationFilter.ALL),
        battleye: BattlEyeHighscoresFilter = Query(None),
        pvp_types: List[PvpTypeFilter] = Query([], alias="pvp"),
) -> TibiaResponse[Highscores]:
    if world.lower() in ("global", "all"):
        world = None
    return await app.state.client.fetch_highscores_page(world, category, page=page, vocation=vocation, battleye_type=battleye,
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


@app.get("/news/recent/{days}")
async def get_recent_news(
    days: int = Path(...),
    types: Set[NewsType] = Query(None, alias="type"),
    categories: Set[NewsCategory] = Query(None, alias="category"),
) -> TibiaResponse[NewsArchive]:
    return await app.state.client.fetch_recent_news(days=days, types=types, categories=categories)


@app.get("/news/{news_id}")
async def get_news_article(
    news_id: int = Path(...)
) -> TibiaResponse[Optional[News]]:
    return await app.state.client.fetch_news(news_id=news_id)


@app.get("/spells")
async def get_spells(
        vocation: VocationSpellFilter = Query(None),
        group: SpellGroup = Query(None),
        type: SpellType = Query(None),
        premium: bool = Query(None),
        sort: SpellSorting = Query(None),
) -> TibiaResponse[SpellsSection]:
    return await app.state.client.fetch_spells(vocation=vocation, group=group, spell_type=type, premium=premium, sort=sort)


@app.get("/spells/{identifier}")
async def get_spell(
    identifier: str = Path(...)
) -> TibiaResponse[Optional[Spell]]:
    return await app.state.client.fetch_spell(identifier)


@app.get("/worlds")
async def get_worlds() -> TibiaResponse[WorldOverview]:
    return await app.state.client.fetch_world_list()


@app.get("/worlds/{name}")
async def get_world(name: str = Path(...)) -> TibiaResponse[Optional[World]]:
    return await app.state.client.fetch_world(name)

