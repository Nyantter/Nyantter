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
from ....services import UserAuthService
from ....snowflake import Snowflake

router = APIRouter()

class UserInfo(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None

class EditRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    header_url: Optional[str] = None
    info: Optional[List[UserInfo]] = None

@limiter.limit("5/minute")
@router.patch(
    "/api/user/edit",
    response_class=JSONResponse,
    summary="ユーザーを編集します。"
)
async def edit(request: Request, body: EditRequest, current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken)):
    """
    ユーザーを編集します。
    """

    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )
    
    info = []
    if body.info is not None:
        for _info in body.info:
            info.append(_info.dict())
    infoData = json.dumps(info)
    
    display_name = body.display_name if body.display_name is not None else current_user.display_name
    description = body.description if body.description is not None else current_user.description
    icon_url = body.icon_url if body.icon_url is not None else current_user.icon_url
    header_url = body.header_url if body.header_url is not None else current_user.header_url
    
    query = f"""
    UPDATE {DataHandler.database['prefix']}users
    SET display_name = $1,
        description = $2,
        icon_url = $3,
        header_url = $4,
        info = $5
    WHERE id = $6
    RETURNING *
    """
    
    row = dict(await conn.fetchrow(
        query, 
        display_name, 
        description, 
        icon_url, 
        header_url, 
        infoData, 
        current_user.id
    ))
    await conn.close()
    
    if row["info"] is not None:
        row["info"] = json.loads(row["info"])
    user = User.model_validate(row)
    if isinstance(user.created_at, datetime):
        user.created_at = user.created_at.isoformat()
    return user