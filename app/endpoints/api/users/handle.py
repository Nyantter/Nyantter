from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

from ....objects import User

import json

router = APIRouter()

@router.get(
    "/api/user/@{handle:str}",
    response_class=JSONResponse,
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

    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    if domain is None:
        row = dict(await conn.fetchrow(
            f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle = $1 AND domain IS NULL",
            handle
        ))
    else:
        row = dict(await conn.fetchrow(
            f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle = $1 AND domain = $2",
            handle, domain
        ))

    if not row:
        await conn.close()
        raise HTTPException(status_code=404, detail="User not found")  

    if row["info"] is not None:
        row["info"] = json.loads(row["info"])
    # Parse row into User object
    user = User.parse_obj(row)

    # Convert created_at to ISO format if it's a datetime object
    if isinstance(user.created_at, datetime):
        user.created_at = user.created_at.isoformat()

    await conn.close()
    return user