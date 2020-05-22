import json
import traceback

from aiohttp import web
from aiohttp.web_routedef import RouteDef

import tibiapy
from tibiapy.utils import try_enum

routes = web.RouteTableDef()


@routes.get('/')
async def home(request):
    content = "<h1>Routes</hº><ul>"
    for route in routes:  # type: RouteDef
        if route.path == "/":
            continue
        content += '<li><a href="{0.path}">{0.handler.__name__}</a></li>'.format(route)
    content += "</ul>"
    return web.Response(text=content, content_type='text/html')


@routes.get('/characters/{name}')
async def get_character(request):
    name = request.match_info['name']
    char = await app["tibiapy"].fetch_character(name)
    return web.Response(text=char.to_json())


@routes.get('/guilds/{name}')
async def get_guild(request):
    name = request.match_info['name']
    char = await app["tibiapy"].fetch_guild(name)
    return web.Response(text=char.to_json())


@routes.get('/worlds/{name}/guilds')
async def get_guilds(request):
    name = request.match_info['name']
    guild_list = await app["tibiapy"].fetch_world_guilds(name)
    return web.Response(text=json.dumps(guild_list, default=dict))


@routes.get(r'/highscores/{world}/{category}/{vocations:\d+}/{page}')
async def get_highscores(request):
    world = request.match_info['world']
    category = request.match_info['category']
    vocations = int(request.match_info['vocations'])
    page = request.match_info['page']
    highscores = await app["tibiapy"].fetch_highscores_page(world,
                                                            try_enum(tibiapy.Category, category,
                                                                     tibiapy.Category.EXPERIENCE),
                                                            try_enum(tibiapy.VocationFilter, vocations,
                                                                     tibiapy.VocationFilter.ALL),
                                                            int(page))
    return web.Response(text=highscores.to_json())


@routes.get('/houses/{world}/{town}')
async def get_houses(request):
    world = request.match_info['world']
    town = request.match_info['town']
    house_list = await app["tibiapy"].fetch_world_houses(world, town)
    return web.Response(text=json.dumps(house_list, default=tibiapy.ListedHouse._try_dict))


@routes.get('/house/{world}/{house_id}')
async def get_house(request):
    world = request.match_info['world']
    house_id = request.match_info['house_id']
    house = await app["tibiapy"].fetch_house(int(house_id), world)
    return web.Response(text=house.to_json())


@routes.get('/killstatistics/{world}')
async def get_kill_statistics(request):
    world = request.match_info['world']
    kill_statistics = await app["tibiapy"].fetch_kill_statistics(world)
    return web.Response(text=kill_statistics.to_json())


@routes.get('/worlds')
async def get_worlds(request):
    worlds = await app["tibiapy"].fetch_world_list()
    return web.Response(text=worlds.to_json())


@routes.get('/worlds/{name}')
async def get_world(request):
    name = request.match_info['name']
    world = await app["tibiapy"].fetch_world(name)
    return web.Response(text=world.to_json())


@routes.get('/news/recent')
async def get_recent_news(request):
    news = await app["tibiapy"].fetch_recent_news()
    return web.Response(text=json.dumps(news, default=tibiapy.ListedNews._try_dict))


@routes.get('/news/{news_id}')
async def get_news(request):
    news_id = request.match_info['news_id']
    news = await app["tibiapy"].fetch_news(int(news_id))
    return web.Response(text=news.to_json())


@routes.get('/news/{news_id}/html')
async def get_news_html(request):
    news_id = request.match_info['news_id']
    news = await app["tibiapy"].fetch_news(int(news_id))
    return web.Response(text=news.content, content_type='text/html')


@routes.get('/tournaments/{tournament_id}')
async def get_tournaments(request):
    tournament_id = request.match_info['tournament_id']
    tournament = await app["tibiapy"].fetch_tournament(int(tournament_id))
    return web.Response(text=tournament.to_json())


@routes.get('/tournaments/{tournament_id}/leaderboards/{world}/{page}')
async def get_tournaments_leaderboard(request):
    tournament_id = request.match_info['tournament_id']
    world = request.match_info['world']
    page = request.match_info['page']
    tournament = await app["tibiapy"].fetch_tournament_leaderboard(int(tournament_id), world, int(page))
    return web.Response(text=tournament.to_json())


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
    async def middleware_handler(request):
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
    app = web.Application(middlewares=[error_middleware])
    app.add_routes(routes)
    app.on_startup.append(init_client)
    print("Registered routes:")
    for route in routes:  # type: RouteDef
        print('\t[%s] %s' % (route.method, route.path))
    web.run_app(app, port=8000)
