from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from .....data import DataHandler
from .....snowflake import Snowflake

import emoji

router = APIRouter()

class CreateReactionRequest(BaseModel):
    reaction: str

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

@router.post(
    "/api/letter/{letter_id:int}/reaction/create",
    response_class=JSONResponse,
    summary="リアクションを作成します。"
)
async def create_reaction(request: CreateReactionRequest, letter_id: int, current_user: dict = Depends(get_current_user)):
    """
    リアクションを作成します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    chkLetter = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE id = $1", letter_id)

    if not chkLetter:
        raise HTTPException(status_code=404, detail="Letter not found")    

    reaction = emoji.demojize(request.reaction)
    if not ":" in reaction:
        raise HTTPException(status_code=400, detail="Reaction not found")

    reaction_id = Snowflake.generate()

    query = f"""
        INSERT INTO {DataHandler.database['prefix']}reactions (id, user_id, letter_id, reaction)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT ON CONSTRAINT unique_user_letter_reaction DO UPDATE
            SET reaction = EXCLUDED.reaction;
    """

    row = await conn.execute(query, reaction_id, current_user["id"], chkLetter["id"], reaction)

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to create reaction")

    await conn.close()
    return {
        "detail": "success"
    }