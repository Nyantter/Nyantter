from ..data import DataHandler
from .reaction import Reaction
from .user import User

from pydantic import BaseModel
from typing import Optional
import asyncpg

class Letter(BaseModel):
    id: int
    created_at: str
    content: Optional[str] = None
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None

    async def getReplys(self) -> list["Letter"]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )

        letters = []
        raw_Letters = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE replyed_to=$1", self.id)

        for letter in raw_Letters:
            letters.append(Letter.model_validate(dict(letter)))

        await conn.close()
        return letters

    async def getReLetteredPosts(self) -> list["Letter"]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )

        letters = []
        raw_Letters = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}letters WHERE relettered_to=$1", self.id)

        for letter in raw_Letters:
            letters.append(Letter.model_validate(dict(letter)))

        await conn.close()
        return letters

    async def getReactions(self) -> list[Reaction]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )

        reactions = []
        raw_Reactions = await conn.fetch(f"SELECT * FROM {DataHandler.database['prefix']}reactions WHERE letter_id=$1", self.id)

        for reaction in raw_Reactions:
            reactions.append(Reaction.model_validate(dict(reaction)))

        await conn.close()
        return reactions

    async def fetchUser(self) -> User:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )
        return (User.model_validate(dict(conn.fetchval(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id=$1", self.id))))