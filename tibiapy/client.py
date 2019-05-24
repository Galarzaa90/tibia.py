import asyncio
import aiohttp

from tibiapy import Character, Guild, World, House, KillStatistics, ListedGuild, Highscores, Category, VocationFilter, \
    ListedHouse, HouseType, WorldOverview


class Client():
    def __init__(self, loop=None, session=None):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop() if loop is None else loop
        if session is not None:
            self.session = session
        self.session = self.loop.run_until_complete(self._initialize_session())

    @classmethod
    async def _initialize_session(cls):
        return aiohttp.ClientSession()

    async def _get(self, url):
        async with self.session.get(url) as resp:
            return await resp.text()

    async def fetch_character(self, name):
        content = await self._get(Character.get_url(name))
        char = Character.from_content(content)
        return char

    async def fetch_guild(self, name):
        content = await self._get(Guild.get_url(name))
        guild = Guild.from_content(content)
        return guild

    async def fetch_house(self, house_id: int, world: str):
        content = await self._get(House.get_url(house_id, world))
        house = House.from_content(content)
        return house

    async def fetch_highscores_page(self, world, category=Category.EXPERIENCE,
                                    vocation=VocationFilter.ALL, page=1):
        content = await self._get(Highscores.get_url(world, category, vocation, page))
        highscores = Highscores.from_content(content)
        return highscores

    async def fetch_kill_statistics(self, world: str):
        content = await self._get(KillStatistics.get_url(world))
        kill_statistics = KillStatistics.from_content(content)
        return kill_statistics

    async def fetch_world(self, name: str):
        content = await self._get(World.get_url(name))
        world = World.from_content(content)
        return world

    async def fetch_world_houses(self, world, town, house_type=HouseType.HOUSE):
        content = await self._get(ListedHouse.get_list_url(world, town, house_type))
        houses = ListedHouse.list_from_content(content)
        return houses

    async def fetch_world_guilds(self, world: str):
        content = await self._get(ListedGuild.get_world_list_url(world))
        guilds = ListedGuild.list_from_content(content)
        return guilds

    async def fetch_world_list(self):
        content = await self._get(WorldOverview.get_url())
        world_overview = WorldOverview.from_content(content)
        return world_overview
