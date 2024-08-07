import asyncpg
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ....data import DataHandler

router = APIRouter()


@router.get(
    "/api/users/count",
    response_class=JSONResponse,
    summary="総ユーザー数を確認します。",
)
async def usersCount():
    """
    総ユーザー数を確認します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"],
    )

    prefix = DataHandler.database["prefix"]
    users = await conn.fetchval(f"SELECT COUNT(*) FROM {prefix}users")
    local = await conn.fetchval(
        f"SELECT COUNT(*) FROM {prefix}users WHERE domain IS NULL"
    )
    fedi = await conn.fetchval(
        f"SELECT COUNT(*) FROM {prefix}users WHERE domain IS NOT NULL"
    )

    await conn.close()
    return {"all": users, "local": local, "fediverse": fedi}
