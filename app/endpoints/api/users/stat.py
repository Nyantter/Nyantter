from ....data import DataHandler

from fastapi import APIRouter
import asyncpg

router = APIRouter()

@router.get(
    "/api/users/count",
    summary="総ユーザー数を確認します。"
)
async def apiIndex():
    """
    総ユーザー数を確認します。
    """
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    prefix = DataHandler.database["prefix"]
    users = await conn.fetchval(f"SELECT COUNT(*) FROM {prefix}users")

    await conn.close()
    return {
        "users": users
    }