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

import json

router = APIRouter()

def isEmoji(char: str):
    return char in emoji.EMOJI_DATA

@router.get(
    "/api/letter/{letter_id:int}",
    response_class=JSONResponse,
    summary="レターの情報を取得します。"
)
async def letter(letter_id: int):
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

    row = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE id = $1", letter_id)
    emojis = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id = $1", letter_id)

    user_data = dict(await conn.fetchrow(f"SELECT * FROM {prefix}users WHERE id = $1", letter["user_id"]))
    if user_data["info"] is not None:
        user_data["info"] = json.loads(user_data["info"])

    if not row:
        raise HTTPException(status_code=404, detail="Letter not found")  

    reactions = []
    for _emoji in emojis:
        _emoji = dict(_emoji)
        
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
        "user_id": row["user_id"],
        "user": user_data,
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
