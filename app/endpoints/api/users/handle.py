import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ....objects import User
from ....services import UserService

router = APIRouter()

@router.get(
    "/api/user/@{handle:str}",
    response_class=JSONResponse,
    response_model=User,
    summary="ユーザーハンドルからユーザーを取得します。"
)
async def getUserByHandle(handle: str):
    """
    ユーザーハンドルからユーザーを取得します。
    Fediverseユーザーを取得するにはハンドルのあとに**@domain.tld**の形式で書きます。
    """
    
    splitedHandle = handle.split("@")
    if len(splitedHandle) <= 1:
        domain = None
    elif len(splitedHandle) == 2:
        handle = splitedHandle[0]
        domain = splitedHandle[1]
    else:
        raise HTTPException(status_code=400, detail='Only "@userHandle" or "@userHandle@domain.tld" handle format is accepted')

    user = await UserService.getUser(handle, domain=domain)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user