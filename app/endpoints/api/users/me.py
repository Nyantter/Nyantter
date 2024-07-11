from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

from ....ratelimiter import limiter
from ....objects import User

from ....objects import AuthorizedUser
from ....services import UserAuthService

import json

router = APIRouter()

@router.get(
    "/api/user/me",
    response_class=JSONResponse,
    summary="トークンからユーザーを取得します。"
)
async def getuserbytoken(request: Request, current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken)):
    """
    トークンからユーザーを取得します。
    """

    if current_user.info is not None:
        current_user.info = json.loads(current_user.info)
    user = current_user.getUser()
    if isinstance(user.created_at, datetime):
        user.created_at = user.created_at.isoformat()
    return user
