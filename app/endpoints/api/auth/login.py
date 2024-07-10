# 作りかけ

from ....data import DataHandler

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import asyncpg
import bcrypt
from pydantic import BaseModel

import random, string

def random_chars(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

class LoginUserData(BaseModel):
    handle: str
    password: str

router = APIRouter()

@router.post(
    "/api/auth/login",
    response_class=JSONResponse,
)
async def login(user: LoginUserData):
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    row = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle_lower = $1", user.handle.lower())

    if row:
        if bcrypt.checkpw(user.password.encode(), row["password"].encode()):
            token = random_chars(30)
            await conn.execute(f"""
                INSERT INTO {DataHandler.database['prefix']}tokens
                (token, permission, user_id)
                VALUES($1, $2, $3)
            """, token, "all", row["id"])

            await conn.close()
            return {"detail": "registed", "user_id": f"{row['id']}", "token": token}
        else:
            await conn.close()
            raise HTTPException(status_code=400, detail="Username or password incorrect")
    else:
        await conn.close()
        raise HTTPException(status_code=400, detail="Username or password incorrect")