import datetime
import json
import logging
import traceback

from aiohttp import web
from aiohttp.web_middlewares import normalize_path_middleware
from aiohttp.web_routedef import RouteDef

import tibiapy
from tibiapy.utils import try_enum

routes = web.RouteTableDef()

logging_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_formatter)
log = logging.getLogger("tibiapy")
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)


class CustomJson:
    """Custom json implementation that handles tibia.py object serialization correctly."""

    @staticmethod
    def dumps(obj, **kwargs):
        """Dumps an object into a JSON string representing it."""
        return json.dumps(obj, default=tibiapy.abc.Serializable._try_dict)

    @staticmethod
    def loads(s, **kwargs):
        """Loads a JSON string into a python object"""
        return json.loads(s, **kwargs)


def json_response(content):
    status = 200 if content and content.data else 404
    return web.json_response(content, status=status, dumps=CustomJson.dumps)


@routes.get('/')
async def home(request: web.Request):
    content = "<h1>Routes</hº><table><tr><th>Name</th><th>Path</th><tr>"
    for route in routes:  # type: RouteDef
        if route.path == "/":
            continue
        content += f'<tr><td>{route.handler.__name__}</td><td><code>{route.path}</code></td></tr>'
    content += "</table>"
    return web.Response(text=content, content_type='text/html')


@routes.get('/auctions')
async def get_current_auctions(request: web.Request):
    page = int(request.query.get("page", 1))
    filters = await filters_from_query(request)
    response = await app["tibiapy"].fetch_current_auctions(page, filters)
    return json_response(response)


async def filters_from_query(request):
    filters = tibiapy.AuctionFilters()
    filters.world = request.query.get("world")
    filters.battleye = try_enum(tibiapy.BattlEyeTypeFilter, request.query.get("battleye"))
    filters.pvp_type = try_enum(tibiapy.PvpTypeFilter, request.query.get("pvp_type"))
    filters.min_level = tibiapy.utils.parse_integer(request.query.get("min_level"), None)
    filters.max_level = tibiapy.utils.parse_integer(request.query.get("max_level"), None)
    filters.vocation = try_enum(tibiapy.VocationAuctionFilter, request.query.get("vocation"))
    filters.skill = try_enum(tibiapy.SkillFilter, request.query.get("skill"))
    filters.min_skill_level = tibiapy.utils.parse_integer(request.query.get("min_skill_level"), None)
    filters.max_skill_level = tibiapy.utils.parse_integer(request.query.get("max_skill_level"), None)
    filters.order_by = try_enum(tibiapy.AuctionOrderBy, request.query.get("order_by"))
    filters.order = try_enum(tibiapy.AuctionOrder, request.query.get("order"))
    filters.search_string = request.query.get("item")
    return filters


@routes.get('/auctions/history')
async def get_auction_history(request: web.Request):
    page = int(request.query.get("page", 1))
    filters = await filters_from_query(request)
    response = await app["tibiapy"].fetch_auction_history(page, filters)
    return json_response(response)


@routes.get('/auctions/{auction_id}')
async def get_auction(request: web.Request):
    auction_id = request.match_info['auction_id']
    fetch_items = int(request.query.get("fetch_items", 0))
    fetch_mounts = int(request.query.get("fetch_mounts", 0))
    fetch_outfits = int(request.query.get("fetch_outfits", 0))
    skip_details = int(request.query.get("skip_details", 0))
    response = await app["tibiapy"].fetch_auction(int(auction_id), fetch_items=fetch_items, fetch_mounts=fetch_mounts,
                                                  fetch_outfits=fetch_outfits, skip_details=skip_details)
    return json_response(response)


@routes.get('/creatures')
async def get_library_creatures(request: web.Request):
    response = await app["tibiapy"].fetch_library_creatures()
    return json_response(response)


@routes.get('/creatures/boosted')
async def get_boosted_creature(request: web.Request):
    response = await app["tibiapy"].fetch_boosted_creature()
    return json_response(response)


@routes.get('/creatures/{name}')
async def get_library_creature(request: web.Request):
    name = request.match_info.get('name')
    response = await app["tibiapy"].fetch_creature(name)
    return json_response(response)


@routes.get('/events')
@routes.get('/events/{year}/{month}')
async def get_event_schedule(request: web.Request):
    year = request.match_info.get('year')
    month = request.match_info.get('month')
    if year:
        year = int(year)
    if month:
        month = int(month)
    response = await app["tibiapy"].fetch_event_schedule(month, year)
    return json_response(response)


@routes.get('/cmposts/{start_date}/{end_date}')
async def get_cm_post_archive(request: web.Request):
    start_date_str = request.match_info['start_date']
    end_date_str = request.match_info['end_date']
    page = int(request.query.get("page", 1))
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    response = await app["tibiapy"].fetch_cm_post_archive(start_date, end_date, page)
    return json_response(response)


@routes.get('/forums/community')
async def get_community_boards(request: web.Request):
    response = await app["tibiapy"].fetch_forum_community_boards()
    return json_response(response)


@routes.get('/forums/support')
async def get_support_boards(request: web.Request):
    response = await app["tibiapy"].fetch_forum_support_boards()
    return json_response(response)


@routes.get('/forums/world')
async def get_world_boards(request: web.Request):
    response = await app["tibiapy"].fetch_forum_world_boards()
    return json_response(response)


@routes.get('/forums/trade')
async def get_trade_boards(request: web.Request):
    response = await app["tibiapy"].fetch_forum_trade_boards()
    return json_response(response)


@routes.get('/forums/thread/{thread_id}')
async def get_forum_thread(request: web.Request):
    thread_id = request.match_info['thread_id']
    page = int(request.query.get("page", 1))
    response = await app["tibiapy"].fetch_forum_thread(int(thread_id), page)
    return json_response(response)


@routes.get('/forums/post/{post_id}')
async def get_forum_post(request: web.Request):
    post_id = request.match_info['post_id']
    response = await app["tibiapy"].fetch_forum_post(int(post_id))
    return json_response(response)


@routes.get('/forums/post/{post_id}/html')
async def get_forum_post_html(request: web.Request):
    post_id = request.match_info['post_id']
    response = await app["tibiapy"].fetch_forum_post(int(post_id))
    return web.Response(text=response.data.anchored_post.content, content_type="text/html")


@routes.get('/forums/announcement/{announcement_id}')
async def get_forum_announcement(request: web.Request):
    announcement_id = request.match_info['announcement_id']
    response = await app["tibiapy"].fetch_forum_announcement(int(announcement_id))
    return json_response(response)


@routes.get('/forums/announcement/{announcement_id}/html')
async def get_forum_announcement_html(request: web.Request):
    announcement_id = request.match_info['announcement_id']
    response = await app["tibiapy"].fetch_forum_announcement(int(announcement_id))
    return json_response(response)


@routes.get('/forums/board/{board_id}')
async def get_board_threads(request: web.Request):
    board_id = request.match_info['board_id']
    page = int(request.query.get("page", 1))
    age = int(request.query.get("age", 30))
    response = await app["tibiapy"].fetch_forum_board(int(board_id), page, age)
    return json_response(response)


@routes.get('/characters/{name}')
async def get_character(request: web.Request):
    name = request.match_info['name']
    response = await app["tibiapy"].fetch_character(name)
    return json_response(response)


@routes.get('/guilds/{name}')
async def get_guild(request: web.Request):
    name = request.match_info['name']
    response = await app["tibiapy"].fetch_guild(name)
    return json_response(response)


@routes.get('/guilds/{name}/wars')
async def get_guild_wars(request: web.Request):
    name = request.match_info['name']
    response = await app["tibiapy"].fetch_guild_wars(name)
    return json_response(response)


@routes.get('/worlds/{name}/guilds')
async def get_world_guilds(request: web.Request):
    name = request.match_info['name']
    response = await app["tibiapy"].fetch_world_guilds(name)
    return json_response(response)


@routes.get(r'/highscores/{world}')
async def get_highscores(request: web.Request):
    world = request.match_info['world']
    category = try_enum(tibiapy.Category, request.query.get("category", "EXPERIENCE").upper(), tibiapy.Category.EXPERIENCE)
    vocations = try_enum(tibiapy.VocationFilter, int(request.query.get("vocation", 0)), tibiapy.VocationFilter.ALL)
    battleye_type = try_enum(tibiapy.BattlEyeHighscoresFilter, int(request.query.get("battleye", -1)))
    page = int(request.query.get("page", 1))
    pvp_params = request.query.getall("pvp", [])
    pvp_types = [try_enum(tibiapy.PvpTypeFilter, param) for param in pvp_params]
    pvp_types = [p for p in pvp_types if p is not None]
    if world.lower() == "all":
        world = None
    response = await app["tibiapy"].fetch_highscores_page(world, category, vocations, page, battleye_type, pvp_types)
    return json_response(response)


@routes.get('/houses/{world}/{town}')
async def get_houses(request: web.Request):
    world = request.match_info['world']
    town = request.match_info['town']
    order = try_enum(tibiapy.HouseOrder, request.query.get("order"), tibiapy.HouseOrder.NAME)
    status = try_enum(tibiapy.HouseStatus, request.query.get("status"))
    house_type = try_enum(tibiapy.HouseType, request.query.get("type"), tibiapy.HouseType.HOUSE)
    response = await app["tibiapy"].fetch_world_houses(world, town, house_type, status, order)
    return json_response(response)


@routes.get('/house/{world}/{house_id}')
async def get_house(request: web.Request):
    world = request.match_info['world']
    house_id = request.match_info['house_id']
    response = await app["tibiapy"].fetch_house(int(house_id), world)
    return json_response(response)


@routes.get('/killstatistics/{world}')
async def get_kill_statistics(request: web.Request):
    world = request.match_info['world']
    response = await app["tibiapy"].fetch_kill_statistics(world)
    return json_response(response)


@routes.get('/leaderboards/{world}')
@routes.get('/leaderboards/{world}/{rotation}')
async def get_leaderboard(request: web.Request):
    world = request.match_info['world']
    rotation = request.match_info.get('rotation')
    page = int(request.query.get("page", 1))
    if rotation:
        rotation = int(rotation)
    response = await app["tibiapy"].fetch_leaderboard(world, rotation, page)
    return json_response(response)


@routes.get('/worlds')
async def get_worlds(request: web.Request):
    response = await app["tibiapy"].fetch_world_list()
    return json_response(response)


@routes.get('/worlds/{name}')
async def get_world(request: web.Request):
    name = request.match_info['name']
    response = await app["tibiapy"].fetch_world(name)
    return json_response(response)


@routes.get('/news/recent')
@routes.get('/news/recent/{days}')
async def get_recent_news(request: web.Request):
    days = request.match_info.get("days")
    if days:
        days = int(days)
    else:
        days = 30
    response = await app["tibiapy"].fetch_recent_news(days)
    return json_response(response)


@routes.get('/news/{news_id}')
async def get_news(request: web.Request):
    news_id = request.match_info['news_id']
    response = await app["tibiapy"].fetch_news(int(news_id))
    return json_response(response)


@routes.get('/news/{news_id}/html')
async def get_news_html(request: web.Request):
    news_id = request.match_info['news_id']
    response = await app["tibiapy"].fetch_news(int(news_id))
    if response and response.data:
        return web.Response(text=response.data.content, content_type="text/html")
    else:
        return web.HTTPNotFound()


@routes.get('/tournaments/{tournament_id}')
async def get_tournaments(request: web.Request):
    tournament_id = request.match_info['tournament_id']
    response = await app["tibiapy"].fetch_tournament(int(tournament_id))
    return json_response(response)


@routes.get('/tournaments/{tournament_id}/leaderboards/{world}/{page}')
async def get_tournaments_leaderboard(request: web.Request):
    tournament_id = request.match_info['tournament_id']
    world = request.match_info['world']
    page = request.match_info['page']
    response = await app["tibiapy"].fetch_tournament_leaderboard(int(tournament_id), world, int(page))
    return json_response(response)


def json_error(status_code: int, exception: Exception, tb=None) -> web.Response:
    return web.Response(
        status=status_code,
        body=json.dumps({
            'error': exception.__class__.__name__,
            'detail': str(exception),
            'stack': tb
        }).encode('utf-8'),
        content_type='application/json')


async def error_middleware(app, handler):
    async def middleware_handler(request: web.Request):
        try:
            response = await handler(request)
            return response
        except web.HTTPException as ex:
            if ex.status == 404:
                return json_error(ex.status, ex)
            raise
        except Exception as e:
            tb = traceback.format_exc()
            log.exception("%s %s", request.method, request.path)
            return json_error(500, e, tb)

    return middleware_handler


async def init_client(app):
    app["tibiapy"] = tibiapy.Client()


async def cleanup_client(app):
    await app["tibiapy"].session.close()


if __name__ == "__main__":
    normalize_paths = normalize_path_middleware(remove_slash=True, append_slash=False)
    app = web.Application(middlewares=[
        error_middleware,
        normalize_paths,
    ])
    app.add_routes(routes)
    app.on_startup.append(init_client)
    app.on_cleanup.append(cleanup_client)
    print("Registered routes:")
    for route in routes:  # type: RouteDef
        print('- %s %s' % (route.method, route.path))
    web.run_app(app, port=8000)
