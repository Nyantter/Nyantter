from ....data import DataHandler
from ....sendmail import MailSender
from ....snowflake import Snowflake

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import asyncpg
import asyncio

import re
from pydantic import BaseModel

import bcrypt
from typing import Optional

import random, string
from email.mime.text import MIMEText

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from ....ratelimiter import limiter

def random_chars(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

router = APIRouter()

class RegisterUserData(BaseModel):
    email: Optional[str] = None
    handle: str
    password: str
    # captchaanswer: str 別の機会に実装

async def deleteToken(token):
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )
    for _ in range(300):
        click = await conn.fetchval(f"""
            SELECT EXISTS (SELECT * FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1)
        """, token)
        if not click:
            await conn.close()
            return
        await asyncio.sleep(1)

    click = await conn.fetchval(f"""
        SELECT EXISTS (SELECT * FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1)
    """, token)

    if click:
        await conn.execute(f"""
            DELETE FROM {DataHandler.database['prefix']}emailcheck WHERE token = $1
        """, token)
    await conn.close()

@limiter.limit("1/hour")
@router.post(
    "/api/auth/register",
    response_class=JSONResponse,
)
async def register(request: Request, background_tasks: BackgroundTasks, user: RegisterUserData):
    if re.match(r"[^\a-zA-Z0-9_]", user.handle):
        raise HTTPException(status_code=400, detail="Username mustn't contain characters other than [a-zA-Z0-9_]")

    if (user.password is None) or (user.password == ""):
        raise HTTPException(status_code=400, detail="Password mustn't be null")

    if (DataHandler.register["emailRequired"]) and ((user.email is None) or (user.email == "")):
        raise HTTPException(status_code=400, detail="Email mustn't be null")

    salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
    user.password = bcrypt.hashpw(user.password.encode(), salt).decode()

    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    if DataHandler.register["emailRequired"]:
        if user.email is None:
            raise HTTPException(status_code=400, detail="Email field is required")

        token = random_chars(30)

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}emailcheck
            (token, email, handle, password, handle_lower)
            VALUES($1, $2, $3, $4, $5)
        """, token, user.email, user.handle, user.password, user.handle.lower())
        await conn.close()
        
        await MailSender.send(
            subject="Registration application has been accepted.",
            to=user.email,
            attach=[
                MIMEText(
                    f"""
                    <html>
                        <body>
                            <h1>Nyantter</h1>
                            <p>To register with {DataHandler.server['name']}, click on the link below.</p><br>
                            <a href="{DataHandler.server['url']}/email-auth/{token}">{DataHandler.server['url']}/email-auth/{token}</a><br>
                            <p>If you do not remember registering, please ignore this email! Your registration will be canceled after 5 minutes!</p><br>
                            <small>Nyantter</small>
                        </body>
                    </html>
                    """,
                    "html",
                    "utf-8"
                )
            ]
        )
        background_tasks.add_task(deleteToken, token)
        return {"detail": "Email has been sent; you must click within 5 minutes to validate your email address."}
    else:
        uniqueid = Snowflake.generate()
        token = random_chars(30)

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
        """, uniqueid, user.email, user.handle, user.password, publicKey.decode('utf8') , privateKey.decode('utf8') )

        await conn.execute(f"""
            INSERT INTO {DataHandler.database['prefix']}tokens
            (token, permission, user_id)
            VALUES($1, $2, $3)
        """, token, "all", uniqueid)
        await conn.close()
        return {"detail": "registed", "user_id": f"{uniqueid}", "token": token}