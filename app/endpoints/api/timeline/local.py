from ....data import DataHandler

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import asyncpg

router = APIRouter()

@router.get(
    "/api/timeline/local",
    response_class=JSONResponse,
    summary="ローカルタイムラインを取得します。"
)
async def localTimeLine(page = Query(default=0, ge=0)):
    """
    ローカルタイムラインを取得します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    prefix = DataHandler.database["prefix"]
    _letters = list(await conn.fetch(f"SELECT * FROM {prefix}letters LIMIT 20 OFFSET $1", page*20))

    letters = []
    for letter in _letters:
        letter = dict(letter)
        letter["id"] = str(letter["id"])
        letters.append(letter)

    await conn.close()
    return {
        "letters": letters,
        "next": f"{DataHandler.server['url']}/api/timeline/local?page={page+1}"
    }