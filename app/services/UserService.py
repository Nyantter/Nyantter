import json
from datetime import datetime
from typing import Optional

import asyncpg

from ..data import DataHandler
from ..objects import User


class UserService:
    @classmethod
    async def getUser(
        cls, handle: str, *, domain: Optional[str] = None
    ) -> Optional[User]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"],
        )
        if domain is None:
            row = await conn.fetchrow(
                f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle_lower = $1 AND domain IS NULL",
                handle.lower(),
            )
        else:
            row = await conn.fetchrow(
                f"SELECT * FROM {DataHandler.database['prefix']}users WHERE handle_lower = $1 AND domain = $2",
                handle.lower(),
                domain.lower(),
            )

        if not row:
            await conn.close()
            return None

        row = dict(row)

        if row["info"] is not None:
            row["info"] = json.loads(row["info"])
        if row["following"] is not None:
            row["following"] = json.loads(row["following"])
        if row["followers"] is not None:
            row["followers"] = json.loads(row["followers"])
        # Parse row into User object
        user = User.model_validate(row)

        # Convert created_at to ISO format if it's a datetime object
        if isinstance(user.created_at, datetime):
            user.created_at = user.created_at.isoformat()

        await conn.close()
        return user

    @classmethod
    async def getUserFromID(cls, id: int) -> Optional[User]:
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"],
        )
        row = await conn.fetchrow(
            f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id = $1", id
        )

        if not row:
            await conn.close()
            return None

        row = dict(row)

        if row["info"] is not None:
            row["info"] = json.loads(row["info"])
        if row["following"] is not None:
            row["following"] = json.loads(row["following"])
        if row["followers"] is not None:
            row["followers"] = json.loads(row["followers"])
        # Parse row into User object
        user = User.model_validate(row)

        # Convert created_at to ISO format if it's a datetime object
        if isinstance(user.created_at, datetime):
            user.created_at = user.created_at.isoformat()

        await conn.close()
        return user
