from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.endpoints import emailauth

from app.endpoints.api import index as APIIndex
from app.endpoints.api.users import stat as UserStat
from app.endpoints.api.auth import register, login
from app.endpoints.api.timeline import local
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
app.include_router(nodeinfo_router)  # 追加
