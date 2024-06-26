from ..data import DataHandler
from .user import User
from pydantic import BaseModel
import asyncpg

class Reaction(BaseModel):
    id: int
    letter_id: int
    user_id: int
    reaction: str

    async def fetchUser(self) -> User:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )
        return (User.model_validate(dict(conn.fetchval(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id=$1", self.id))))