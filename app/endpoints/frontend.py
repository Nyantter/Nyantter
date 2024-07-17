from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..services import LetterService, UserService
from ..data import DataHandler

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    template_name = "index.html"
    return templates.TemplateResponse(template_name, {"request": request})


@router.get("/timeline", response_class=HTMLResponse)
async def timeline(request: Request):
    template_name = "timeline.html"
    return templates.TemplateResponse(template_name, {"request": request})


@router.get("/@{handle:str}", response_class=HTMLResponse)
async def user(request: Request, handle: str):
    splitedHandle = handle.split("@")
    if len(splitedHandle) <= 1:
        domain = None
    elif len(splitedHandle) == 2:
        handle = splitedHandle[0]
        domain = splitedHandle[1]
    else:
        raise HTTPException(
            status_code=404,
            detail="エラーページは実装できてません！ｗ",
        )

    user = await UserService.getUser(handle, domain=domain)
    if not user:
        raise HTTPException(
            status_code=404, detail="エラーページは実装できてません！ｗ"
        )

    template_name = "user.html"
    return templates.TemplateResponse(
        template_name, {"request": request, "user": user, "DataHandler": DataHandler}
    )


@router.get("/@{handle:str}/letter/{letter_id:int}", response_class=HTMLResponse)
async def user_letter(request: Request, handle: str, letter_id: int):
    letter = await LetterService.getLetter(letter_id)
    if not letter:
        raise HTTPException(
            status_code=404, detail="エラーページは実装できてません！ｗ"
        )

    template_name = "letter.html"
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "letter": letter,
            "DataHandler": DataHandler,
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    template_name = "login.html"
    return templates.TemplateResponse(template_name, {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    template_name = "register.html"
    return templates.TemplateResponse(template_name, {"request": request})
