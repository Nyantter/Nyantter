from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
from contextlib import asynccontextmanager

from app.endpoints import emailauth
from app.endpoints.api import index as APIIndex
from app.endpoints.api.users import stat as UserStat
from app.endpoints.api.auth import register, login
from app.endpoints.api.timeline import local
from app.endpoints.api.letter.edit import router as edit_letter_router
from app.endpoints.api.letter.create import router as create_letter_router  # 追加
from app.endpoints.api.letter.delete import router as delete_letter_router  # 追加
from app.endpoints.api.letter.letter import router as letter_router  # 追加
from app.endpoints.api.letter.reaction.create import router as create_reaction_router  # 追加
from app.endpoints.api.letter.reaction.delete import router as delete_reaction_router  # 追加
from app.endpoints.wellknown.nodeinfo import router as nodeinfo_router  # 追加

log = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Nyantter started.")
    yield
    log.info("Nyantter is shutdowning...")

app = FastAPI(lifespan=lifespan)

app.include_router(emailauth.router)
app.include_router(APIIndex.router)
app.include_router(UserStat.router)
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
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    with open("static/timeline.html", "r", encoding="utf8") as f:
        return HTMLResponse(f.read())

@app.get("/timeline", response_class=HTMLResponse, include_in_schema=False)
async def timeline():
    with open("static/timeline.html", "r", encoding="utf8") as f:
        return HTMLResponse(f.read())

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login():
    with open("static/login.html", "r", encoding="utf8") as f:
        return HTMLResponse(f.read())

@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register():
    with open("static/register.html", "r", encoding="utf8") as f:
        return HTMLResponse(f.read())
