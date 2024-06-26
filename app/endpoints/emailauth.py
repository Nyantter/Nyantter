# 作りかけ

from ..data import DataHandler
from ..snowflake import Snowflake

from fastapi import APIRouter
import asyncpg

router = APIRouter()

@router.get(
    "/email-auth/{token:str}",
)
async def emailauth(token: str):
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    row = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1", token)

    print(row)

    if row:
        await conn.execute(f"""
            DELETE FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1
        """, token)

        uniqueid = Snowflake.generate()

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}users
            (id, email, handle, password)
            VALUES($1, $2, $3, $4)
        """, uniqueid, row["email"], row["handle"], row["password"])

        await conn.close()
        return {"detail": "registed", "userid": f"{uniqueid}"}
    else:
        await conn.close()
        return {"detail": "invalid"}