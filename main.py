# Import necessary modules and routers
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from contextlib import asynccontextmanager
import asyncpg
import aiofiles
from app.data import DataHandler

# Import endpoint routers
from app.endpoints import emailauth
from app.endpoints.api import index
from app.endpoints.api.users import stat, handle, me
from app.endpoints.api.auth import register, login
from app.endpoints.api.timeline import local
from app.endpoints.api.letter.edit import router as edit_letter_router
from app.endpoints.api.letter.create import router as create_letter_router
from app.endpoints.api.letter.delete import router as delete_letter_router
from app.endpoints.api.letter.letter import router as letter_router
from app.endpoints.api.letter.reaction.create import router as create_reaction_router
from app.endpoints.api.letter.reaction.delete import router as delete_reaction_router
from app.endpoints.wellknown.nodeinfo import router as nodeinfo_router

from app.endpoints import frontend

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
        database=DataHandler.database["name"]
    )
    await conn.execute(f"DELETE FROM {DataHandler.database['prefix']}emailcheck WHERE created_at > NOW() + INTERVAL '5 minutes';")
    await conn.close()
    log.info("Nyantter started.")
    yield
    log.info("Nyantter is shutting down...")

# Initialize app
app = FastAPI(
    name="Nyantter",
    lifespan=lifespan
)

# Register routers
app.include_router(emailauth.router)
app.include_router(index.router)
app.include_router(stat.router)
app.include_router(handle.router)
app.include_router(me.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(local.router)
app.include_router(create_letter_router)
app.include_router(edit_letter_router)
app.include_router(delete_letter_router)
app.include_router(letter_router)
app.include_router(create_reaction_router)
app.include_router(delete_reaction_router)
app.include_router(nodeinfo_router)

app.include_router(frontend.router)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")