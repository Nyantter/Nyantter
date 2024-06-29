from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

router = APIRouter()

class EditLetterRequest(BaseModel):
    content: str
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

@router.patch(
    "/api/letter/{letter_id:int}/edit",
    response_class=JSONResponse,
    summary="レターを編集します。"
)
async def create_letter(request: EditLetterRequest, letter_id: int, current_user: dict = Depends(get_current_user)):
    """
    レターを編集します。
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
    elif chkLetter["user_id"] != current_user["id"]:
        raise HTTPException(status_code=400, detail="That letter is not yours")      

    edited_at = datetime.now()

    query = f"""
        UPDATE {DataHandler.database['prefix']}letters
        SET content = $1, attachments = $2, edited_at = $3
        WHERE id = $4 AND user_id = $5
        RETURNING id, created_at, edited_at, content, replyed_to, relettered_to, attachments
    """

    row = await conn.fetchrow(query, request.content, request.attachments, edited_at, letter_id, current_user['id'])

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to edit letter")

    letter = {
        "id": row["id"],
        "created_at": row["created_at"].isoformat(),  # ISO 8601形式の文字列に変換
        "edited_at": row["edited_at"].isoformat(),
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"]
    }

    await conn.close()
    return letter
