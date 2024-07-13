import json
from datetime import datetime
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....data import DataHandler
from ....objects import AuthorizedUser, User
from ....ratelimiter import limiter
from ....services import UserAuthService
from ....snowflake import Snowflake

router = APIRouter()


@router.get(
    "/api/user/me",
    response_class=JSONResponse,
    summary="トークンからユーザーを取得します。",
)
async def getuserbytoken(
    request: Request,
    current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken),
):
    """
    トークンからユーザーを取得します。
    """

    if current_user.info is not None:
        current_user.info = json.loads(current_user.info)
    user = current_user.getUser()
    if isinstance(user.created_at, datetime):
        user.created_at = user.created_at.isoformat()
    return user
