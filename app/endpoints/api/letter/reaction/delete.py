from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from .....data import DataHandler
from .....snowflake import Snowflake

router = APIRouter()

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

@router.delete(
    "/api/letter/{letter_id:int}/reaction/delete",
    response_class=JSONResponse,
    summary="リアクションを削除します。"
)
async def create_reaction(letter_id: int, current_user: dict = Depends(get_current_user)):
    """
    リアクションを削除します。
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
    
    chkReaction = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE user_id = $1 AND letter_id = $2", current_user["id"], letter_id)
    
    if not chkReaction:
        raise HTTPException(status_code=404, detail="Reaction not found")

    reaction_id = Snowflake.generate()

    query = f"""
        DELETE FROM {DataHandler.database['prefix']}reactions
        WHERE letter_id = $1 AND user_id = $2
    """

    row = await conn.execute(query, chkLetter["id"], current_user["id"])

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to delete reaction")

    await conn.close()
    return {
        "detail": "success"
    }
