import json
import logging
import traceback
import datetime

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


@routes.get('/')
async def home(request: web.Request):
    content = "<h1>Routes</hº><ul>"
    for route in routes:  # type: RouteDef
        if route.path == "/":
            continue
        content += '<li><a href="{0.path}">{0.handler.__name__}</a></li>'.format(route)
    content += "</ul>"
    return web.Response(text=content, content_type='text/html')


@routes.get('/auctions/')
async def get_current_auctions(request: web.Request):
    page = int(request.query.get("page", 1))
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
    filters.item = request.query.get("item")
    auctions = await app["tibiapy"].fetch_current_auctions(page, filters)
    return web.json_response(auctions, dumps=CustomJson.dumps)


@routes.get('/auctions/history')
async def get_auction_history(request: web.Request):
    boosted = await app["tibiapy"].fetch_auction_history()
    return web.json_response(boosted, dumps=CustomJson.dumps)


@routes.get('/auctions/{auction_id}')
async def get_auction(request: web.Request):
    auction_id = request.match_info['auction_id']
    fetch_items = int(request.query.get("fetch_items", 0))
    fetch_mounts = int(request.query.get("fetch_mounts", 0))
    fetch_outfits = int(request.query.get("fetch_outfits", 0))
    skip_details = int(request.query.get("skip_details", 0))
    boosted = await app["tibiapy"].fetch_auction(int(auction_id), fetch_items=fetch_items, fetch_mounts=fetch_mounts,
                                                 fetch_outfits=fetch_outfits, skip_details=skip_details)
    return web.json_response(boosted, dumps=CustomJson.dumps)


@routes.get('/boostedcreature/')
async def get_boosted_creature(request: web.Request):
    boosted = await app["tibiapy"].fetch_boosted_creature()
    return web.json_response(boosted, dumps=CustomJson.dumps)


@routes.get('/events/')
@routes.get('/events/{year}/{month}')
async def get_event_schedule(request: web.Request):
    year = request.match_info.get('year')
    month = request.match_info.get('month')
    if year:
        year = int(year)
    if month:
        month = int(month)
    calendar = await app["tibiapy"].fetch_event_schedule(month, year)
    return web.json_response(calendar, dumps=CustomJson.dumps)


@routes.get('/cmposts/{start_date}/{end_date}/')
async def get_cm_post_archive(request: web.Request):
    start_date_str = request.match_info['start_date']
    end_date_str = request.match_info['end_date']
    page = int(request.query.get("page", 1))
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
    cm_post_archive = await app["tibiapy"].fetch_cm_post_archive(start_date, end_date, page)
    return web.json_response(cm_post_archive, dumps=CustomJson.dumps)


@routes.get('/forums/community/')
async def get_community_boards(request: web.Request):
    boards = await app["tibiapy"].fetch_forum_community_boards()
    return web.json_response(boards, dumps=CustomJson.dumps)


@routes.get('/forums/support/')
async def get_support_boards(request: web.Request):
    boards = await app["tibiapy"].fetch_forum_support_boards()
    return web.json_response(boards, dumps=CustomJson.dumps)


@routes.get('/forums/world/')
async def get_world_boards(request: web.Request):
    boards = await app["tibiapy"].fetch_forum_world_boards()
    return web.json_response(boards, dumps=CustomJson.dumps)


@routes.get('/forums/trade/')
async def get_trade_boards(request: web.Request):
    boards = await app["tibiapy"].fetch_forum_trade_boards()
    return web.json_response(boards, dumps=CustomJson.dumps)


@routes.get('/forums/thread/{thread_id}')
async def get_forum_thread(request: web.Request):
    thread_id = request.match_info['thread_id']
    page = int(request.query.get("page", 1))
    thread = await app["tibiapy"].fetch_forum_thread(int(thread_id), page)
    return web.json_response(thread, dumps=CustomJson.dumps)


@routes.get('/forums/post/{post_id}')
async def get_forum_post(request: web.Request):
    post_id = request.match_info['post_id']
    post = await app["tibiapy"].fetch_forum_post(int(post_id))
    return web.json_response(post, dumps=CustomJson.dumps)


@routes.get('/forums/announcement/{announcement_id}/')
async def get_forum_announcement(request: web.Request):
    announcement_id = request.match_info['announcement_id']
    announcement = await app["tibiapy"].fetch_forum_announcement(int(announcement_id))
    return web.json_response(announcement, dumps=CustomJson.dumps)


@routes.get('/forums/announcement/{announcement_id}/html/')
async def get_forum_announcement_html(request: web.Request):
    announcement_id = request.match_info['announcement_id']
    announcement = await app["tibiapy"].fetch_forum_announcement(int(announcement_id))
    return web.Response(text=announcement.data.content, content_type="text/html")


@routes.get('/forums/board/{board_id}/')
async def get_board_threads(request: web.Request):
    board_id = request.match_info['board_id']
    page = int(request.query.get("page", 1))
    age = int(request.query.get("age", 30))
    board = await app["tibiapy"].fetch_forum_board(int(board_id), page, age)
    return web.json_response(board, dumps=CustomJson.dumps)


@routes.get('/characters/{name}/')
async def get_character(request: web.Request):
    name = request.match_info['name']
    char = await app["tibiapy"].fetch_character(name)
    return web.json_response(char, dumps=CustomJson.dumps)


@routes.get('/guilds/{name}/')
async def get_guild(request: web.Request):
    name = request.match_info['name']
    guild = await app["tibiapy"].fetch_guild(name)
    return web.json_response(guild, dumps=CustomJson.dumps)


@routes.get('/guilds/{name}/wars/')
async def get_guild_wars(request: web.Request):
    name = request.match_info['name']
    guild_wars = await app["tibiapy"].fetch_guild_wars(name)
    return web.json_response(guild_wars, dumps=CustomJson.dumps)


@routes.get('/worlds/{name}/guilds/')
async def get_world_guilds(request: web.Request):
    name = request.match_info['name']
    guild_list = await app["tibiapy"].fetch_world_guilds(name)
    return web.json_response(guild_list, dumps=CustomJson.dumps)


@routes.get(r'/highscores/{world}/')
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
    highscores = await app["tibiapy"].fetch_highscores_page(world, category, vocations, page, battleye_type, pvp_types)
    return web.json_response(highscores, dumps=CustomJson.dumps)


@routes.get('/houses/{world}/{town}/')
async def get_houses(request: web.Request):
    world = request.match_info['world']
    town = request.match_info['town']
    order = try_enum(tibiapy.HouseOrder, request.query.get("order"), tibiapy.HouseOrder.NAME)
    status = try_enum(tibiapy.HouseStatus, request.query.get("status"))
    house_type = try_enum(tibiapy.HouseType, request.query.get("type"), tibiapy.HouseType.HOUSE)
    house_list = await app["tibiapy"].fetch_world_houses(world, town, house_type, status, order)
    return web.json_response(house_list, dumps=CustomJson.dumps)


@routes.get('/house/{world}/{house_id}/')
async def get_house(request: web.Request):
    world = request.match_info['world']
    house_id = request.match_info['house_id']
    house = await app["tibiapy"].fetch_house(int(house_id), world)
    return web.json_response(house, dumps=CustomJson.dumps)


@routes.get('/killstatistics/{world}/')
async def get_kill_statistics(request: web.Request):
    world = request.match_info['world']
    kill_statistics = await app["tibiapy"].fetch_kill_statistics(world)
    return web.json_response(kill_statistics, dumps=CustomJson.dumps)


@routes.get('/worlds/')
async def get_worlds(request: web.Request):
    worlds = await app["tibiapy"].fetch_world_list()
    return web.json_response(worlds, dumps=CustomJson.dumps)


@routes.get('/worlds/{name}/')
async def get_world(request: web.Request):
    name = request.match_info['name']
    world = await app["tibiapy"].fetch_world(name)
    return web.json_response(world, dumps=CustomJson.dumps)


@routes.get('/news/recent/')
@routes.get('/news/recent/{days}')
async def get_recent_news(request: web.Request):
    days = request.match_info.get("days")
    if days:
        days = int(days)
    else:
        days = 30
    news = await app["tibiapy"].fetch_recent_news(days)
    return web.json_response(news, dumps=CustomJson.dumps)


@routes.get('/news/{news_id}/')
async def get_news(request: web.Request):
    news_id = request.match_info['news_id']
    news = await app["tibiapy"].fetch_news(int(news_id))
    return web.json_response(news, dumps=CustomJson.dumps)


@routes.get('/news/{news_id}/html/')
async def get_news_html(request: web.Request):
    news_id = request.match_info['news_id']
    news = await app["tibiapy"].fetch_news(int(news_id))
    return web.Response(text=news.data.content, content_type='text/html')


@routes.get('/tournaments/{tournament_id}/')
async def get_tournaments(request: web.Request):
    tournament_id = request.match_info['tournament_id']
    tournament = await app["tibiapy"].fetch_tournament(int(tournament_id))
    return web.json_response(tournament, dumps=CustomJson.dumps)


@routes.get('/tournaments/{tournament_id}/leaderboards/{world}/{page}/')
async def get_tournaments_leaderboard(request: web.Request):
    tournament_id = request.match_info['tournament_id']
    world = request.match_info['world']
    page = request.match_info['page']
    tournament = await app["tibiapy"].fetch_tournament_leaderboard(int(tournament_id), world, int(page))
    return web.json_response(tournament, dumps=CustomJson.dumps)


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
            if response.status == 404:
                return json_error(response.status, Exception(response.message))
            return response
        except web.HTTPException as ex:
            if ex.status == 404:
                return json_error(ex.status, ex)
            raise
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            return json_error(500, e, tb)

    return middleware_handler


async def init_client(app):
    app["tibiapy"] = tibiapy.Client()

if __name__ == "__main__":
    normalize_paths = normalize_path_middleware()
    app = web.Application(middlewares=[error_middleware, normalize_paths])
    app.add_routes(routes)
    app.on_startup.append(init_client)
    print("Registered routes:")
    for route in routes:  # type: RouteDef
        print('\t[%s] %s' % (route.method, route.path))
    web.run_app(app, port=8000)
