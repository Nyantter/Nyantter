from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from contextlib import asynccontextmanager

from app.endpoints import emailauth
from app.endpoints.api import index as APIIndex
from app.endpoints.api.users import stat as UserStat
from app.endpoints.api.users import handle as UserFromHandle
from app.endpoints.api.users import me as UserFromToken
from app.endpoints.api.auth import register, login
from app.endpoints.api.timeline import local
from app.endpoints.api.letter.edit import router as edit_letter_router
from app.endpoints.api.letter.create import router as create_letter_router  # 追加
from app.endpoints.api.letter.delete import router as delete_letter_router  # 追加
from app.endpoints.api.letter.letter import router as letter_router  # 追加
from app.endpoints.api.letter.reaction.create import router as create_reaction_router  # 追加
from app.endpoints.api.letter.reaction.delete import router as delete_reaction_router  # 追加
from app.endpoints.wellknown.nodeinfo import router as nodeinfo_router  # 追加

import asyncpg
from app.data import DataHandler

import aiofiles

log = logging.getLogger("uvicorn")

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
    log.info("Nyantter is shutdowning...")

app = FastAPI(
    name="Nyantter",
    lifespan=lifespan
)

app.include_router(emailauth.router)
app.include_router(APIIndex.router)
app.include_router(UserStat.router)
app.include_router(UserFromHandle.router)
app.include_router(UserFromToken.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(local.router)
app.include_router(create_letter_router)  # 追加
app.include_router(edit_letter_router)
app.include_router(delete_letter_router)
app.include_router(letter_router)
app.include_router(create_reaction_router)
app.include_router(delete_reaction_router)
app.include_router(nodeinfo_router)  # 追加

# Static files setup
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint setup
@app.api_route("/", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def root():
    async with aiofiles.open("pages/index.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@app.api_route("/timeline", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def timeline():
    async with aiofiles.open("pages/timeline.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@app.api_route("/login", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def login():
    async with aiofiles.open("pages/login.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@app.api_route("/register", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def register():
    async with aiofiles.open("pages/register.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())
