from __future__ import annotations

import datetime
import logging
from contextlib import asynccontextmanager
from typing import Annotated, Optional, TypeVar

import uvicorn
from fastapi import Depends, FastAPI, Path, Query, Response
from starlette import status

import tibiapy
from tibiapy.enums import (
    AuctionBattlEyeFilter,
    AuctionOrderBy,
    AuctionOrderDirection,
    AuctionSearchType,
    AuctionSkillFilter,
    AuctionVocationFilter,
    HighscoresBattlEyeType,
    HighscoresCategory,
    HighscoresProfession,
    HouseOrder,
    HouseStatus,
    HouseType,
    NewsCategory,
    NewsType,
    PvpTypeFilter,
    SpellGroup,
    SpellSorting,
    SpellType,
    SpellVocationFilter,
)
from tibiapy.models import (
    Auction,
    AuctionFilters,
    BoostableBosses,
    BossEntry,
    Character,
    CharacterBazaar,
    Creature,
    CreatureEntry,
    CreaturesSection,
    EventSchedule,
    FansitesSection,
    ForumBoard,
    ForumSection,
    ForumThread,
    Guild,
    GuildsSection,
    GuildWars,
    Highscores,
    House,
    HousesSection,
    KillStatistics,
    Leaderboard,
    News,
    NewsArchive,
    Spell,
    SpellsSection,
    TibiaResponse,
    World,
    WorldOverview,
)

logging_formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
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

T = TypeVar("T")


def handle_response(response: Response, body: T) -> T:
    """Change the status code to 404 if no data is returned in the response."""
    if isinstance(body, TibiaResponse) and body.data is None:
        response.status_code = status.HTTP_404_NOT_FOUND

    return body


@app.get("/healthcheck", tags=["General"])
async def healthcheck() -> bool:
    return True


# region News

FROM_DESCRIPTION = "Only show articles published on this date or after."
TO_DESCRIPTION = "Only show articles published on this date or before."
TYPES_DESCRIPTION = "The types of news to display. Leave empty to show any."
CATEGORIES_DESCRIPTION = "The categories of news to display. Leave empty to show any."


@app.get("/news/{news_id:int}", tags=["News"])
async def get_news_article(
        response: Response,
        news_id: int = Path(..., description="The ID of the news entry to see."),
) -> TibiaResponse[Optional[News]]:
    return handle_response(response, await app.state.client.fetch_news(news_id=news_id))


@app.get("/news/{fromDate}", tags=["News"],
         summary="Get news archive from date")
async def get_news_archive(
        response: Response,
        from_date: datetime.date = Path(..., alias="fromDate", description=FROM_DESCRIPTION),
        types: set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    """Show the news archive from a start date to today."""
    return handle_response(response, await app.state.client.fetch_news_archive(from_date, None, categories, types))


@app.get("/news/{fromDate}/{toDate}", tags=["News"],
         summary="Get news archive between dates")
async def get_news_archive_between_dates(
        response: Response,
        from_date: datetime.date = Path(..., alias="fromDate", description=FROM_DESCRIPTION),
        to_date: datetime.date = Path(..., alias="toDate", description=TO_DESCRIPTION),
        types: set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    """Show the news archive for a specific date period."""
    return handle_response(response, await app.state.client.fetch_news_archive(from_date, to_date, categories, types))


@app.get("/news", tags=["News"])
async def get_news_archive_by_days(
        response: Response,
        days: int = Query(30, description="The number of days to look back for news."),
        types: set[NewsType] = Query(None, alias="type", description=TYPES_DESCRIPTION),
        categories: set[NewsCategory] = Query(None, alias="category", description=CATEGORIES_DESCRIPTION),
) -> TibiaResponse[NewsArchive]:
    return handle_response(response, await app.state.client.fetch_news_archive_by_days(days, categories, types))


@app.get("/events/", tags=["News"])
async def get_current_events_schedule() -> TibiaResponse[EventSchedule]:
    """Get the event calendar for the current month."""
    return await app.state.client.fetch_event_schedule()


@app.get("/events/{year}/{month}", tags=["News"])
async def get_events_schedule(
        year: int = Path(...),
        month: int = Path(..., ge=1, le=12),
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
        response: Response,
        vocation: Optional[SpellVocationFilter] = Query(None,
                                                        description="Only show spells that this vocation can learn."),
        group: SpellGroup = Query(None, description="Only show spells in this group."),
        type: SpellType = Query(None, description="Only show spells of this type."),
        is_premium: bool = Query(None, alias="isPremium",
                                 description="If true, only show premium spells, "
                                             "if false, only show free account spells. "
                                             "Otherwise, show all."),
        sort: SpellSorting = Query(None, description="The sort order to use."),
) -> TibiaResponse[SpellsSection]:
    return handle_response(
        response,
        await app.state.client.fetch_spells(
            vocation=vocation,
            group=group,
            spell_type=type,
            is_premium=is_premium,
            sort=sort,
        ),
    )


@app.get("/library/spells/{identifier}", tags=["Library"])
async def get_spell(
        response: Response,
        identifier: str = Path(...,
                               description="The spell's identifier. "
                                           "This is usually the spell's name in lowercase and no spaces."),
) -> TibiaResponse[Optional[Spell]]:
    return handle_response(response, await app.state.client.fetch_spell(identifier))


# endregion

# region Community


@app.get("/characters/{name}", tags=["Community"])
async def get_character(
        name: str = Path(...),
) -> TibiaResponse[Optional[Character]]:
    return await app.state.client.fetch_character(name)


@app.get("/worlds", tags=["Community"])
async def get_worlds(response: Response) -> TibiaResponse[WorldOverview]:
    return handle_response(response, await app.state.client.fetch_world_overview())


@app.get("/worlds/{name}", tags=["Community"])
async def get_world(
        response: Response,
        name: str = Path(..., description="The name of the world."),
) -> TibiaResponse[Optional[World]]:
    return handle_response(response, await app.state.client.fetch_world(name))


@app.get("/guilds/{name}", tags=["Community"])
async def get_guild(
        name: str = Path(...),
) -> TibiaResponse[Optional[Guild]]:
    return await app.state.client.fetch_guild(name)


@app.get("/guilds/{name}/wars", tags=["Community"])
async def get_guild_wars(
        name: str = Path(...),
) -> TibiaResponse[Optional[GuildWars]]:
    return await app.state.client.fetch_guild_wars(name)


@app.get("/worlds/{world}/guilds", tags=["Community"])
async def get_world_guilds(
        world: str = Path(...),
) -> TibiaResponse[Optional[GuildsSection]]:
    return await app.state.client.fetch_world_guilds(world)


@app.get("/highscores/{world}", tags=["Community"])
async def get_highscores(
        world: str = Path(...),
        page: int = Query(1),
        category: HighscoresCategory = Query(HighscoresCategory.EXPERIENCE),
        vocation: HighscoresProfession = Query(HighscoresProfession.ALL),
        battleye: HighscoresBattlEyeType = Query(None),
        pvp_types: list[PvpTypeFilter] = Query([], alias="pvp"),
) -> TibiaResponse[Highscores]:
    if world.lower() in {"global", "all"}:
        world = None

    return await app.state.client.fetch_highscores_page(world, category, page=page, vocation=vocation,
                                                        battleye_type=battleye,
                                                        pvp_types=pvp_types)


@app.get("/houses/{world}/{houseId:int}", tags=["Community"])
async def get_house(
        response: Response,
        world: str = Path(..., description="The world where the house is located."),
        house_id: int = Path(..., alias="houseId", description="The ID of the house."),
) -> TibiaResponse[Optional[House]]:
    return handle_response(response, await app.state.client.fetch_house(house_id, world))


@app.get("/houses/{world}/{town}", tags=["Community"])
async def get_houses_section(
        world: str = Path(..., description="The world to search in."),
        town: str = Path(..., description="The game town to search in."),
        status: HouseStatus = Query(None, description="The house status to filter houses by. Empty will show any."),
        order: HouseOrder = Query(None, description="The field or value to order results by."),
        house_type: HouseType = Query(None, alias="type", description="The type of house to show."),
) -> TibiaResponse[Optional[HousesSection]]:
    return await app.state.client.fetch_houses_section(world, town, status=status, order=order, house_type=house_type)


@app.get("/killStatistics/{world}", tags=["Community"])
@app.get("/killstatistics/{world}", tags=["Community"])
async def get_kill_statistics(
        world: str = Path(...),
) -> TibiaResponse[Optional[KillStatistics]]:
    return await app.state.client.fetch_kill_statistics(world)


@app.get("/leaderboards/{world}", tags=["Community"])
async def get_leaderboard(
        response: Response,
        world: str = Path(..., description="The world to see the leaderboard of."),
        page: int = Query(1, description="The page to display."),
        rotation_id: int = Query(None, alias="rotationId",
                                 description="The ID of the rotation to see, leave empty to see latest.\n"
                                             "Note that it's only possible to see the current and previous rotations."),
) -> TibiaResponse[Optional[Leaderboard]]:
    """Show the latest Tibiadrome rotation's leaderboard."""
    return handle_response(
        response,
        await app.state.client.fetch_leaderboard(world=world, rotation=rotation_id, page=page),
    )


@app.get("/fansites", tags=["Community"])
async def get_fansites(
        response: Response,
) -> TibiaResponse[FansitesSection]:
    """Show the fansites section."""
    return handle_response(
        response,
        await app.state.client.fetch_fansites_section(),
    )


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
        section_id: int = Path(...),
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

def auction_filter_parameters(
        world: str = Query(None, description="Show only auctions from this world."),
        pvp_type: PvpTypeFilter = Query(None, alias="pvpType",
                                        description="Show only auctions from characters in worlds of this PvP Type."),
        battleye: AuctionBattlEyeFilter = Query(
            None, alias="battleyeType",
            description="Show only auctions from characters in worlds with this type of BattlEye protection.",
        ),
        vocation: AuctionVocationFilter = Query(None,
                                                description="Show only auctions of characters of this vocation."),
        min_level: int = Query(None, alias="minLevel", ge=0, description="The minimum level to display."),
        max_level: int = Query(None, alias="maxLevel", ge=0, description="The maximum level to display."),
        skill: AuctionSkillFilter = Query(None, description="The skill to filter by its level range."),
        min_skill_level: int = Query(None, alias="minSkillLevel", ge=0,
                                     description="The minimum skill level to display."),
        max_skill_level: int = Query(None, alias="maxSkillLevel", ge=0,
                                     description="The maximum skill level to display."),
        order_by: AuctionOrderBy = Query(None, alias="orderBy", description="The column or value to order by."),
        order: AuctionOrderDirection = Query(None, alias="orderDirection", description="The ordering direction."),
        search_string: str = Query(None, alias="searchString", description="The search term to filter out auctions."),
        search_type: AuctionSearchType = Query(None, alias="searchType", description="The type of search to use."),
) -> AuctionFilters:
    return AuctionFilters(
        world=world,
        pvp_type=pvp_type,
        battleye=battleye,
        vocation=vocation,
        min_level=min_level,
        max_level=max_level,
        skill=skill,
        min_skill_level=min_skill_level,
        max_skill_level=max_skill_level,
        order_by=order_by,
        order=order,
        search_string=search_string,
        search_type=search_type,
    )


@app.get("/auctions/", tags=["Char Bazaar"])
async def get_current_auctions(
        page: int = Query(1),
        filters: Annotated[AuctionFilters, Depends(auction_filter_parameters)] = None,
) -> TibiaResponse[CharacterBazaar]:
    return await app.state.client.fetch_current_auctions(
        page,
        filters,
    )


@app.get("/auctions/history/", tags=["Char Bazaar"])
async def get_auctions_history(
        page: int = Query(1),
        filters: Annotated[AuctionFilters, Depends(auction_filter_parameters)] = None,
) -> TibiaResponse[CharacterBazaar]:
    return await app.state.client.fetch_auction_history(page, filters)


@app.get("/auctions/{auction_id}", tags=["Char Bazaar"])
async def get_auction(
        auction_id: int = Path(...),
        skip_details: bool = Query(
            False,
            description="Whether to skip the auction details and only fetch the basic information.",
        ),
        fetch_items: bool = Query(False, description="Whether to fetch additional item pages (if available)."),
        fetch_mounts: bool = Query(False, description="Whether to fetch additional mounts pages (if available)."),
        fetch_outfits: bool = Query(False, description="Whether to fetch additional outfits pages (if available)."),
        fetch_familiars: bool = Query(False, description="Whether to fetch additional familiars pages (if available)."),
) -> TibiaResponse[Optional[Auction]]:
    return await app.state.client.fetch_auction(auction_id, skip_details=skip_details, fetch_items=fetch_items,
                                                fetch_mounts=fetch_mounts, fetch_outfits=fetch_outfits,
                                                fetch_familiars=fetch_familiars)


# endregion


if __name__ == "__main__":
    uvicorn.run(app=app)
