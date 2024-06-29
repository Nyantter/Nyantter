from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake  # 追加

router = APIRouter()

class CreateLetterRequest(BaseModel):
    content: str
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None
    attachments: Optional[dict] = None

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
    "/api/letter/create",
    response_class=JSONResponse,
    summary="新しいレターを作成します。"
)
async def create_letter(request: CreateLetterRequest, current_user: dict = Depends(get_current_user)):
    """
    新しいレターを作成します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    letter_id = Snowflake.generate()  # SnowflakeでIDを生成
    created_at = datetime.utcnow().isoformat()

    query = f"""
    INSERT INTO {DataHandler.database['prefix']}letters (id, created_at, content, replyed_to, relettered_to, attachments, user_id)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    RETURNING id, created_at, content, replyed_to, relettered_to, attachments
    """

    row = await conn.fetchrow(query, letter_id, created_at, request.content, request.replyed_to, request.relettered_to, request.attachments, current_user['id'])

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to create letter")

    letter = {
        "id": row["id"],
        "created_at": row["created_at"],
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"]
    }

    await conn.close()
    return letter
