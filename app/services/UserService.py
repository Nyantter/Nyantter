import asyncpg
from ..data import DataHandler
from ..objects import User
from typing import Optional
from datetime import datetime
import json

class UserService:
    @classmethod
    async def getUser(cls, handle: str, *, domain: Optional[str]=None) -> Optional[User]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )
        if domain is None:
            row = await conn.fetchrow(
                f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle_lower = $1 AND domain IS NULL",
                handle.lower()
            )
        else:
            row = await conn.fetchrow(
                f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle_lower = $1 AND domain = $2",
                handle.lower(), domain.lower()
            )

        if not row:
            await conn.close()
            return None
        
        row = dict(row)

        if row["info"] is not None:
            row["info"] = json.loads(row["info"])
        # Parse row into User object
        user = User.model_validate(row)

        # Convert created_at to ISO format if it's a datetime object
        if isinstance(user.created_at, datetime):
            user.created_at = user.created_at.isoformat()

        await conn.close()
        return user