import asyncpg
from . import UserService
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

        row["user"] = await UserService.getUserFromID(row["user_id"])

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
        letter = Letter.model_validate(row)
        if isinstance(letter.created_at, datetime):
            letter.created_at = letter.created_at.isoformat()
        if isinstance(letter.edited_at, datetime):
            letter.edited_at = letter.edited_at.isoformat()
        return letter