import asynctest
from aioresponses import aioresponses

from tests.tests_character import FILE_CHARACTER_RESOURCE
from tests.tests_tibiapy import TestCommons
from tibiapy import Client, Character


class TestClient(asynctest.TestCase, TestCommons):
    def setUp(self):
        self.client = Client()

    async def tearDown(self):
        await self.client.session.close()

    @aioresponses()
    async def testFetchCharacter(self, mock_get):
        content = self._load_resource(FILE_CHARACTER_RESOURCE)
        mock_get.get(Character.get_url("Tschas"), status=200, body=content)
        character = await self.client.fetch_character("Tschas")

        self.assertIsInstance(character, Character)
