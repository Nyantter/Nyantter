from datetime import datetime
from typing import List, Optional, Union
import json

import asyncpg
from pydantic import BaseModel

from ..data import DataHandler


class User(BaseModel):
    id: int
    created_at: Union[datetime, str]
    handle: str
    handle_lower: str
    domain: Optional[str] = None
    display_name: Optional[str] = None
    icon_url: Optional[str] = None
    header_url: Optional[str] = None
    description: Optional[str] = None
    info: Optional[List[dict]] = None
    following: List[int]
    followers: List[int]
    public_key: str

    async def follow(self, target: "User") -> bool:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"],
        )
        if self.id in target.followers:
            target.followers.remove(self.id)
            await conn.execute(
                f"""
                UPDATE {DataHandler.database['prefix']}users
                SET followers = $1
                WHERE id = $2
                """,
                json.dumps(target.followers),
                target.id,
            )
            self.following.remove(target.id)
            await conn.execute(
                f"""
                UPDATE {DataHandler.database['prefix']}users
                SET following = $1
                WHERE id = $2
                """,
                json.dumps(self.following),
                self.id,
            )
            return False
        else:
            target.followers.append(self.id)
            await conn.execute(
                f"""
                UPDATE {DataHandler.database['prefix']}users
                SET followers = $1
                WHERE id = $2
                """,
                json.dumps(target.followers),
                target.id,
            )
            self.following.append(target.id)
            await conn.execute(
                f"""
                UPDATE {DataHandler.database['prefix']}users
                SET following = $1
                WHERE id = $2
                """,
                json.dumps(self.following),
                self.id,
            )
            return True
