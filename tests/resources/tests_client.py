import asyncio

from tests.tests_tibiapy import TestTibiaPy
from tibiapy import Client


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestClient(TestTibiaPy):
    def setUp(self):
        self.client = Client()

    @async_test
    async def testFetchCharacter(self):
        pass
