import asyncio
import datetime
import logging
import random

import tibiapy

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))

log = logging.getLogger("tibia.py")
log.setLevel(logging.INFO)
log.addHandler(console_handler)


async def main():
    log.info("Initializing client")
    client = tibiapy.Client()
    try:
        log.info("Fetching world list...")
        response = await client.fetch_world_list()
        assert isinstance(response, tibiapy.TibiaResponse)
        assert isinstance(response.data, tibiapy.WorldOverview)
        log.info(f"{len(response.data.worlds)} worlds found.")
        assert isinstance(response.data.record_count, int)
        assert response.data.record_count > 0
        assert isinstance(response.data.record_date, datetime.datetime)

        selected = random.choice(response.data.regular_worlds)
        assert isinstance(selected, tibiapy.ListedWorld)
        log.info(f"World {selected.name} selected: {selected.online_count} online | {selected.pvp_type}"
                 f" | {selected.location}")
        assert isinstance(selected.pvp_type, tibiapy.PvpType)
        assert isinstance(selected.location, tibiapy.WorldLocation)
        log.info("Fetching world...")
        response = await client.fetch_world(selected.name)
        assert isinstance(response.data, tibiapy.World)

    finally:
        await client.session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
