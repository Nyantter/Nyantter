import json
import re
from datetime import datetime
from typing import Optional

import asyncpg
import emoji
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse

from ....data import DataHandler

router = APIRouter()


def isEmoji(char: str):
    return char in emoji.EMOJI_DATA


@router.get(
    "/api/timeline/local",
    response_class=JSONResponse,
    summary="ローカルタイムラインを取得します。",
)
async def localTimeLine(
    page: int = Query(default=0, ge=0), since: Optional[str] = None
):
    """
    ローカルタイムラインを取得します。
    """

    if since is None:
        since = datetime(2000, 1, 1)
    else:
        since = datetime.strptime(since, "%Y-%m-%dT%H:%M:%S.%f%z")

    conn: asyncpg.Connection = await asyncpg.connect(
        host=DataHandler.database["host"],
        port=DataHandler.database["port"],
        user=DataHandler.database["user"],
        password=DataHandler.database["pass"],
        database=DataHandler.database["name"],
    )

    prefix = DataHandler.database["prefix"]
    _letters = await conn.fetch(
        f"SELECT * FROM {prefix}letters WHERE created_at > $1 ORDER BY created_at DESC LIMIT 20 OFFSET $2",
        since,
        page * 20,
    )

    letters = []
    for letter in _letters:
        letter = dict(letter)
        if letter.get("domain") is not None:
            continue
        user_data = dict(
            await conn.fetchrow(
                f"SELECT * FROM {prefix}users WHERE id = $1", letter["user_id"]
            )
        )
        if user_data["info"] is not None:
            user_data["info"] = json.loads(user_data["info"])
        del user_data["email"]
        del user_data["password"]
        del user_data["private_key"]
        letter["user"] = user_data
        emojis = await conn.fetch(
            f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id = $1",
            letter["id"],
        )
        letter["id"] = str(letter["id"])

        reactions = []
        for _emoji in emojis:
            _emoji = dict(_emoji)
            pattern = r"^:([A-Za-z0-9_]+):$"
            match = re.match(pattern, _emoji["reaction"])

            if not isEmoji(_emoji["reaction"]) and match is not None:
                moji = match.group(1)
                if not isEmoji(emoji.emojize(f":{moji}:")):
                    chkEmoji = dict(
                        await conn.fetchrow(
                            f"SELECT * FROM {DataHandler.database['prefix']}emojis WHERE id = $1",
                            moji,
                        )
                    )
                    if chkEmoji:
                        chkEmoji["type"] = "custom"
                        _emoji["reaction_data"] = chkEmoji
                    else:
                        _emoji = None
                else:
                    _emoji["reaction_data"] = {
                        "type": "normal",
                        "emoji": emoji.emojize(f":{moji}:"),
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
        "next": f"{DataHandler.server['url']}/api/timeline/local?page={page+1}",
    }
