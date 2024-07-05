from ....data import DataHandler

from fastapi import APIRouter, Query, Depends, Header
from fastapi.responses import JSONResponse
import asyncpg

import emoji
import re

from datetime import datetime

from typing import Optional

router = APIRouter()

def isEmoji(char: str):
    return char in emoji.EMOJI_DATA

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
    "/api/timeline/local",
    response_class=JSONResponse,
    summary="ローカルタイムラインを取得します。"
)
async def localTimeLine(page: int = Query(default=0, ge=0), since:str = None, user: Depends(get_current_user)):
    """
    ローカルタイムラインを取得します。
    """
    
    if user is None:
        user_id = None
    else:
        user_id = user.get("id", None)
    
    if since is None:
        since = datetime(2000, 1, 1)
    else:
        since = datetime.strptime(since, '%Y-%m-%dT%H:%M:%S.%f%z')
    
    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"]
    )

    prefix = DataHandler.database["prefix"]
    _letters = list(await conn.fetch(f"SELECT * FROM {prefix}letters WHERE created_at > $1 ORDER BY created_at DESC LIMIT 20 OFFSET $2", since, page*20))

    letters = []
    for letter in _letters:
        user = dict(await conn.fetchrow(f"SELECT * FROM {prefix}users WHERE id = $1", letter["user_id"]))
        if user.get("domain") is not None:
            continue
        del user["email"]
        del user["password"]
        del user["private_key"]
        letter = dict(letter)
        letter["user"] = user
        emojis = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id = $1", letter["id"])
        letter["id"] = str(letter["id"])

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
                    chkEmoji = dict(await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}emojis WHERE id = $1", moji))
                    if chkEmoji:
                        chkEmoji["type"] = "custom"
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

        letter["reactions"] = reactions

        letters.append(letter)

    await conn.close()
    return {
        "letters": letters,
        "next": f"{DataHandler.server['url']}/api/timeline/local?page={page+1}"
    }