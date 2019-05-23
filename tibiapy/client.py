import asyncio
import aiohttp

from tibiapy import Character


class Client():
    def __init__(self, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop

    async def fetch_character(self, name):
        async with aiohttp.ClientSession() as session:
            async with session.get(Character.get_url(name)) as resp:
                content = await resp.text()
                char = Character.from_content(content)
                return char
