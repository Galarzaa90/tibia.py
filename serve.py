import json

from aiohttp import web

import tibiapy
from tibiapy.utils import try_enum

routes = web.RouteTableDef()


@routes.get('/character/{name}')
async def get_character(request: web.Request):
    name = request.match_info['name']
    char = await app["tibiapy"].fetch_character(name)
    return web.Response(text=char.to_json())


@routes.get('/guild/{name}')
async def get_guild(request: web.Request):
    name = request.match_info['name']
    char = await app["tibiapy"].fetch_guild(name)
    return web.Response(text=char.to_json())


@routes.get('/guilds/{name}')
async def get_guilds(request: web.Request):
    name = request.match_info['name']
    guild_list = await app["tibiapy"].fetch_world_guilds(name)
    return web.Response(text=json.dumps(guild_list, default=dict))


@routes.get('/highscores/{world}/{category}/{vocations}/{page}')
async def get_highscores(request: web.Request):
    world = request.match_info['world']
    category = request.match_info['category']
    vocations = request.match_info['vocations']
    page = request.match_info['page']
    highscores = await app["tibiapy"].fetch_highscores_page(world,
                                                            try_enum(tibiapy.Category, category,
                                                                     tibiapy.Category.EXPERIENCE),
                                                            try_enum(tibiapy.VocationFilter, vocations,
                                                                     tibiapy.VocationFilter.ALL),
                                                            int(page))
    return web.Response(text=highscores.to_json())


@routes.get('/houses/{world}/{town}')
async def get_houses(request: web.Request):
    world = request.match_info['world']
    town = request.match_info['town']
    house_list = await app["tibiapy"].fetch_world_houses(world, town)
    return web.Response(text=json.dumps(house_list, default=tibiapy.ListedHouse._try_dict))


@routes.get('/house/{world}/{house_id}')
async def get_house(request: web.Request):
    world = request.match_info['world']
    house_id = request.match_info['house_id']
    house = await app["tibiapy"].fetch_house(int(house_id), world)
    return web.Response(text=house.to_json())


@routes.get('/killstatistics/{world}')
async def get_kill_statistics(request: web.Request):
    world = request.match_info['world']
    kill_statistics = await app["tibiapy"].fetch_kill_statistics(world)
    return web.Response(text=kill_statistics.to_json())


@routes.get('/worlds')
async def get_worlds(request: web.Request):
    worlds = await app["tibiapy"].fetch_world_list()
    return web.Response(text=worlds.to_json())


@routes.get('/world/{name}')
async def get_worlds(request: web.Request):
    name = request.match_info['name']
    world = await app["tibiapy"].fetch_world(name)
    return web.Response(text=world.to_json())


async def init_client(app):
    app["tibiapy"] = tibiapy.Client()


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(init_client)
    print("Registered routes:")
    for route in routes:
        print('\t[%s] %s' % (route.method, route.path))
    web.run_app(app, port=8000)
