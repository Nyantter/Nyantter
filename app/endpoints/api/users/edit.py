from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional, List
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

from ....ratelimiter import limiter
from ....objects import User

import json

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

async def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # "Bearer <token>"
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    user_id = await conn.fetchval(f"SELECT user_id FROM {DataHandler.database['prefix']}tokens WHERE token = $1", token)

    if not user_id:
        await conn.close()
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id = $1", user_id)

    if not user:
        await conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    await conn.close()
    return dict(user)

@limiter.limit("5/minute")
@router.patch(
    "/api/user/edit",
    response_class=JSONResponse,
    summary="ユーザーを編集します。"
)
async def edit(request: Request, body: EditRequest, current_user: dict = Depends(get_current_user)):
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
    
    display_name = body.display_name if body.display_name is not None else current_user.get("display_name")
    description = body.description if body.description is not None else current_user.get("description")
    icon_url = body.icon_url if body.icon_url is not None else current_user.get("icon_url")
    header_url = body.header_url if body.header_url is not None else current_user.get("header_url")
    
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
    
    row = await conn.fetchrow(
        query, 
        display_name, 
        description, 
        icon_url, 
        header_url, 
        infoData, 
        current_user["id"]
    )
    await conn.close()
    
    user = User.parse_obj(dict(row))
    if isinstance(user.created_at, datetime):
        user.created_at = user.created_at.isoformat()
    return user