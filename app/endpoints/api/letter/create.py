import html
from datetime import datetime
from typing import Optional

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....data import DataHandler
from ....objects import AuthorizedUser
from ....ratelimiter import limiter
from ....services import UserAuthService, WebSocketService
from ....snowflake import Snowflake

router = APIRouter()


class CreateLetterRequest(BaseModel):
    content: str
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None
    attachments: Optional[dict] = None


@limiter.limit("30/minute")
@router.post(
    "/api/letter/create",
    response_class=JSONResponse,
    summary="新しいレターを作成します。",
)
async def create_letter(
    backgroundTask: BackgroundTasks,
    request: Request,
    letter: CreateLetterRequest,
    current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken),
):
    """
    新しいレターを作成します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"],
    )

    letter.content = html.escape(
        letter.content.replace("\r\n", "\n").replace("\r", "\n")
    )

    letter_id = Snowflake.generate()  # SnowflakeでIDを生成
    created_at = datetime.now()

    query = f"""
    INSERT INTO {DataHandler.database['prefix']}letters (id, created_at, content, replyed_to, relettered_to, attachments, user_id, domain)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    RETURNING id, created_at, edited_at, content, replyed_to, relettered_to, attachments, domain
    """

    row = await conn.fetchrow(
        query,
        letter_id,
        created_at,
        letter.content,
        letter.replyed_to,
        letter.relettered_to,
        letter.attachments,
        current_user.id,
        None,
    )

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to create letter")

    letter = {
        "id": row["id"],
        "domain": row["domain"],
        "created_at": row["created_at"].isoformat(),  # ISO 8601形式の文字列に変換
        "edited_at": (row["edited_at"].isoformat() if row["edited_at"] else None),
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"],
    }

    await conn.close()
    backgroundTask.add_task(WebSocketService().broadcastLetter, row["id"])
    return letter
