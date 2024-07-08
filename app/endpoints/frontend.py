import aiofiles
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

# HTML response endpoints
@router.api_route("/", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def root():
    async with aiofiles.open("pages/index.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@router.api_route("/timeline", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def timeline():
    async with aiofiles.open("pages/timeline.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@router.api_route("/@{handle:str}", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def user():
    async with aiofiles.open("pages/user.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@router.api_route("/@{handle:str}/letter/{letter_id:int}", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def user_letter():
    async with aiofiles.open("pages/letter.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@router.api_route("/login", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def login():
    async with aiofiles.open("pages/login.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())

@router.api_route("/register", methods=['GET', 'HEAD'], response_class=HTMLResponse, include_in_schema=False)
async def register():
    async with aiofiles.open("pages/register.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())