# Import necessary modules and routers
import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.data import DataHandler
from app.endpoints.api.auth.login import router as login_router
from app.endpoints.api.auth.register import router as register_router
from app.endpoints.api.index import router as index_router
from app.endpoints.api.letter.create import router as create_letter_router
from app.endpoints.api.letter.delete import router as delete_letter_router
from app.endpoints.api.letter.edit import router as edit_letter_router
from app.endpoints.api.letter.letter import router as letter_router
from app.endpoints.api.letter.reaction.create import router as create_reaction_router
from app.endpoints.api.letter.reaction.delete import router as delete_reaction_router
from app.endpoints.api.timeline.local import router as local_router
from app.endpoints.api.users.edit import router as edit_router
from app.endpoints.api.users.handle import router as handle_router
from app.endpoints.api.users.me import router as me_router
from app.endpoints.api.users.stat import router as stat_router
from app.endpoints.emailauth import router as emailauth_router
from app.endpoints.frontend import router as frontend_router
from app.endpoints.websocket import router as ws_router
from app.endpoints.wellknown.nodeinfo import router as nodeinfo_router
from app.endpoints.wellknown.user import router as wk_user_router
from app.endpoints.wellknown.webfinger import router as webfinger_router

# Set up logging
log = logging.getLogger("uvicorn")


# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"],
    )
    await conn.execute(
        f"DELETE FROM {DataHandler.database['prefix']}emailcheck WHERE created_at > NOW() + INTERVAL '5 minutes';"
    )
    await conn.close()
    log.info("Nyantter started.")
    yield
    log.info("Nyantter is shutting down...")


# Initialize app
app = FastAPI(
    title="Nyantter",
    summary="A new SNS",
    description="# A New SNS",
    version="v2024.06.26β",
    lifespan=lifespan,
)

# Register routers
app.include_router(emailauth_router)
app.include_router(ws_router)
app.include_router(index_router)
app.include_router(stat_router)
app.include_router(handle_router)
app.include_router(me_router)
app.include_router(edit_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(local_router)
app.include_router(create_letter_router)
app.include_router(edit_letter_router)
app.include_router(delete_letter_router)
app.include_router(letter_router)
app.include_router(create_reaction_router)
app.include_router(delete_reaction_router)
app.include_router(nodeinfo_router)
app.include_router(webfinger_router)
app.include_router(wk_user_router)
app.include_router(frontend_router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
