from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

router = APIRouter()

@router.get(
    "/api/letter/{letter_id:int}",
    response_class=JSONResponse,
    summary="レターの情報を取得します。"
)
async def letter(letter_id: int):
    """
    レターの情報を取得します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    row = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE id = $1", letter_id)
    emojis = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id = $1", letter_id)

    if not row:
        raise HTTPException(status_code=404, detail="Letter not found")  

    letter = {
        "id": row["id"],
        "created_at": row["created_at"].isoformat(),  # ISO 8601形式の文字列に変換
        "edited_at": row["edited_at"].isoformat() if row["edited_at"] is not None else None,
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"],
        "emojis": emojis,
    }

    await conn.close()
    return letter
