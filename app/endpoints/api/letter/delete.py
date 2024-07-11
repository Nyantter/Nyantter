from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import Response
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake
from ....objects import AuthorizedUser
from ....services import UserAuthService

router = APIRouter()

@router.delete(
    "/api/letter/{letter_id:int}/delete",
    response_class=Response,
    summary="レターを削除します。"
)
async def delete_letter(letter_id: int, current_user: AuthorizedUser = Depends(UserAuthService.getUserFromBearerToken)):
    """
    レターを削除します。
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
    elif chkLetter["user_id"] != current_user.id:
        raise HTTPException(status_code=400, detail="That letter is not yours")      
    query = f"""
        DELETE FROM {DataHandler.database['prefix']}letters
        WHERE id = $1 AND user_id = $2
    """

    row = await conn.execute(query, letter_id, current_user.id)

    if not row:
        await conn.close()
        raise HTTPException(status_code=500, detail="Failed to delete letter")

    await conn.close()
    return None
