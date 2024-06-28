# 作りかけ

from ..data import DataHandler
from ..snowflake import Snowflake

from fastapi import APIRouter
import asyncpg

import random, string

import rsa

def random_chars(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

router = APIRouter()

@router.get(
    "/email-auth/{token:str}",
    include_in_schema=False
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

    if row:
        await conn.execute(f"""
            DELETE FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1
        """, token)

        uniqueid = Snowflake.generate()

        publicKey, privateKey = rsa.newkeys(1024)

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}users
            (id, email, handle, password, public_key, private_key)
            VALUES($1, $2, $3, $4, $5, $6)
        """, uniqueid, row["email"], row["handle"], row["password"], publicKey.save_pkcs1().decode('utf8') , privateKey.save_pkcs1().decode('utf8') )

        token = random_chars(30)

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}tokens
            (token, permission, user_id)
            VALUES($1, $2, $3)
        """, token, "all", uniqueid)

        await conn.close()
        return {"detail": "registed", "user_id": f"{uniqueid}", "token": token}
    else:
        await conn.close()
        return {"detail": "invalid"}