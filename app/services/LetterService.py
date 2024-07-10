import asyncpg
from ..data import DataHandler
from ..objects import Letter
from typing import Optional
from datetime import datetime
import json
import emoji
import re
import logging

class LetterService:
    def isEmoji(char: str):
        return char in emoji.EMOJI_DATA

    @classmethod
    async def getLetter(cls, letter_id: int) -> Optional[Letter]:
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
            return None
        row = dict(row)

        user_data = dict(await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id = $1", row["user_id"]))
        if user_data["info"] is not None:
            user_data["info"] = json.loads(user_data["info"])
        row["user"] = user_data

        reactions = []
        for _emoji in emojis:
            _emoji = dict(_emoji)
            
            pattern = r'^:([A-Za-z0-9_]+):$'
            match = re.match(pattern, _emoji["reaction"])

            if not cls.isEmoji(_emoji["reaction"]) and match is not None:
                moji = match.group(1)
                if not cls.isEmoji(emoji.emojize(f":{moji}:")):
                    chkEmoji = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}emojis WHERE id = $1", moji)
                    if chkEmoji:
                        _emoji["reaction_data"] = dict(chkEmoji)
                    else:
                        _emoji = None
                else:
                    _emoji["reaction_data"] = {
                        "type": "normal",
                        "emoji": emoji.emojize(f":{moji}:")
                    }
            elif cls.isEmoji(_emoji["reaction"]):
                _emoji["reaction_data"] = {
                    "type": "normal",
                    "emoji": _emoji["reaction"],
                }
            reactions.append(_emoji)
        row["reactions"] = reactions
        logging.getLogger("uvicorn").info(row)
        letter = Letter.model_validate(row)
        return letter