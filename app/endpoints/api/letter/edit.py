import html
from datetime import datetime
from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ....data import DataHandler
from ....objects import AuthorizedUser
from ....services import UserAuthService

router = APIRouter()


class EditLetterRequest(BaseModel):
    content: str
    attachments: Optional[dict] = None


@router.patch(
    "/api/letter/{letter_id:int}/edit",
    response_class=JSONResponse,
    summary="レターを編集します。",
)
async def edit_letter(
    request: EditLetterRequest,
    letter_id: int,
    current_user: AuthorizedUser = Depends(
        UserAuthService.getUserFromBearerToken
    ),
):
    """
    レターを編集します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"],
    )

    chkLetter = await conn.fetchrow(
        f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE id = $1",
        letter_id,
    )

    if not chkLetter:
        raise HTTPException(status_code=404, detail="Letter not found")
    elif chkLetter["user_id"] != current_user.id:
        raise HTTPException(status_code=400, detail="That letter is not yours")

    request.content = html.escape(
        request.content.replace("\r\n", "\n").replace("\r", "\n")
    )

    edited_at = datetime.now()

    query = f"""
        UPDATE {DataHandler.database['prefix']}letters
        SET content = $1, attachments = $2, edited_at = $3
        WHERE id = $4 AND user_id = $5
        RETURNING id, created_at, edited_at, content, replyed_to, relettered_to, attachments
    """

    row = await conn.fetchrow(
        query,
        request.content,
        request.attachments,
        edited_at,
        letter_id,
        current_user.id,
    )

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to edit letter")

    letter = {
        "id": row["id"],
        "created_at": row[
            "created_at"
        ].isoformat(),  # ISO 8601形式の文字列に変換
        "edited_at": row["edited_at"].isoformat(),
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"],
    }

    await conn.close()
    return letter
