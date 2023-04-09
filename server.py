import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Path, Query

import tibiapy
from tibiapy import VocationSpellFilter, SpellGroup, SpellType, SpellSorting


logging_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_formatter)
log = logging.getLogger("tibiapy")
log.addHandler(console_handler)
log.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = tibiapy.Client()
    yield
    app.state.client.session.close()

app = FastAPI(lifespan=lifespan)


@app.get("/worlds")
async def get_world():
    return await app.state.client.fetch_world_list()


@app.get("/worlds/{name}")
async def get_world(name: str = Path(...)):
    return await app.state.client.fetch_world(name)


@app.get("/spells")
async def get_spells(
        vocation: VocationSpellFilter = Query(None),
        group: SpellGroup = Query(None),
        type: SpellType = Query(None),
        premium: bool = Query(None),
        sort: SpellSorting = Query(None),
):
    return await app.state.client.fetch_spells(vocation=vocation, group=group, spell_type=type, premium=premium, sort=sort)


@app.get("/spells/{identifier}")
async def get_spell(
    identifier: str = Path(...)
):
    return await app.state.client.fetch_spell(identifier)