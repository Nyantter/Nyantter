# 作りかけ

from ..data import DataHandler
from ..snowflake import Snowflake

from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse
import asyncpg

import random, string

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def random_chars(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

router = APIRouter()

@router.get(
    "/email-auth/{token:str}",
    response_class=RedirectResponse,
    include_in_schema=False
)
async def emailauth(response: Response, token: str):
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

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        privateKey = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        # 鍵をPEM形式でエクスポート（パブリックキー）
        publicKey = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}users
            (id, email, handle, password, public_key, private_key)
            VALUES($1, $2, $3, $4, $5, $6)
        """, uniqueid, row["email"], row["handle"], row["password"], publicKey.decode('utf8') , privateKey.decode('utf8') )

        token = random_chars(30)

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}tokens
            (token, permission, user_id)
            VALUES($1, $2, $3)
        """, token, "all", uniqueid)

        await conn.close()
        response.set_cookie(key="token", value="token", path="/")
        return RedirectResponse("/timeline")
    else:
        await conn.close()
        return {"detail": "invalid"}