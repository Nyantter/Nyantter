from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import asyncpg
from ....services import LetterService
from ....objects import Letter
from ....data import DataHandler

router = APIRouter()

@router.get(
    "/api/letter/{letter_id:int}",
    response_class=JSONResponse,
    response_model=Letter,
    summary="レターの情報を取得します。"
)
async def letterinfo(letter_id: int):
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

    letter = await LetterService.getLetter(letter_id)

    return letter
