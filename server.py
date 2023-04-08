from contextlib import asynccontextmanager

from fastapi import FastAPI, Path

import tibiapy


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