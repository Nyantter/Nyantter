from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.endpoints.api import index
from app.endpoints.api.users import stat

log = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Nyantter started.")
    yield
    log.info("Nyantter is shutdowning...")

app = FastAPI(lifespan=lifespan)

app.include_router(index.router)
app.include_router(stat.router)