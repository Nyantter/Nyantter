import json
from datetime import datetime
from typing import List, Optional

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....data import DataHandler
from ....objects import AuthorizedUser, User
from ....ratelimiter import limiter
from ....services import UserAuthService, UserFollowService, UserService
from ....snowflake import Snowflake

router = APIRouter()


@limiter.limit("30/minute")
@router.patch(
    "/api/user/{user_id:str}/follow",
    response_class=JSONResponse,
    summary="ユーザーをフォローします。",
)
async def follow(
    request: Request,
    handle: str,
    current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken),
):
    """
    ユーザーをフォローします。
    リクエストを送るたびにフォロー/アンフォローが切り替わります。
    """

    target = await UserService.getUser(handle, domain=None)

    return {"follow": await current_user.follow(target)}
