from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
from datetime import datetime

from ....data import DataHandler
from ....snowflake import Snowflake

import emoji
import re

router = APIRouter()

def isEmoji(char: str):
    return char in emoji.EMOJI_DATA

from fastapi import FastAPI, Depends, Header, HTTPException
import asyncpg
from typing import Optional

app = FastAPI()

class DataHandler:
    database = {
        "host": "localhost",
        "port": 5432,
        "user": "user",
        "pass": "password",
        "name": "dbname",
        "prefix": "myapp_"
    }

async def get_current_user(authorization: Optional[str] = Header(None)):
    if authorization is None:
        return None

    try:
        token = authorization.split(" ")[1]  # "Bearer <token>"
    except IndexError:
        return None

    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    user_id = await conn.fetchval(f"SELECT user_id FROM {DataHandler.database['prefix']}tokens WHERE token = $1", token)

    if not user_id:
        await conn.close()
        return None

    user = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id = $1", user_id)

    await conn.close()

    if not user:
        return None

    return dict(user)

@router.get(
    "/api/letter/{letter_id:int}",
    response_class=JSONResponse,
    summary="レターの情報を取得します。"
)
async def letter(letter_id: int, user: Depends(get_current_user)):
    """
    レターの情報を取得します。
    """
    
    if not user:
        user_id = None
    else:
        user_id = user.get("id", None)
    
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    row = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE id = $1", letter_id)
    emojis = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id = $1", letter_id)

    if not row:
        raise HTTPException(status_code=404, detail="Letter not found")  

    reactions = []
    for _emoji in emojis:
        _emoji = dict(_emoji)
        
        if _emoji.get("user_id", 0) == user_id:
            _emoji["ismine"] = True
        else:
            _emoji["ismine"] = False
        
        pattern = r'^:([A-Za-z0-9_]+):$'
        match = re.match(pattern, _emoji["reaction"])

        if not isEmoji(_emoji["reaction"]) and match is not None:
            moji = match.group(1)
            if not isEmoji(emoji.emojize(f":{moji}:")):
                chkEmoji = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}emojis WHERE id = $1", moji)
                if chkEmoji:
                    _emoji["reaction_data"] = chkEmoji
                else:
                    _emoji = None
            else:
                _emoji["reaction_data"] = {
                    "type": "normal",
                    "emoji": emoji.emojize(f":{moji}:")
                }
        elif isEmoji(_emoji["reaction"]):
            _emoji["reaction_data"] = {
                "type": "normal",
                "emoji": _emoji["reaction"],
            }
        reactions.append(_emoji)

    letter = {
        "id": row["id"],
        "created_at": row["created_at"].isoformat(),  # ISO 8601形式の文字列に変換
        "edited_at": row["edited_at"].isoformat() if row["edited_at"] is not None else None,
        "content": row["content"],
        "replyed_to": row["replyed_to"],
        "relettered_to": row["relettered_to"],
        "attachments": row["attachments"],
        "emojis": reactions,
    }

    await conn.close()
    return letter
