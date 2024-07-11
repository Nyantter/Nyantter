from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, Security, Header
from ..data import DataHandler
from ..objects import AuthorizedUser
import asyncpg
import json

class UserAuthService:
    @classmethod
    async def getUserFromBearerToken(cls, bearer: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
        if bearer is None:
            raise HTTPException(
                status_code=401,
                detail="Bearer authentication required",
                headers={'WWW-Authenticate': 'Bearer realm="auth_required"'},
            )
        
        conn: asyncpg.Connection = await asyncpg.connect(
            host=DataHandler.database["host"],
            port=DataHandler.database["port"],
            user=DataHandler.database["user"],
            password=DataHandler.database["pass"],
            database=DataHandler.database["name"]
        )

        user_id = await conn.fetchval(f"SELECT user_id FROM {DataHandler.database['prefix']}tokens WHERE token = $1", bearer.credentials)

        if not user_id:
            await conn.close()
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user = await conn.fetchrow(f"SELECT * FROM {DataHandler.database['prefix']}users WHERE id = $1", user_id)

        if not user:
            await conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        await conn.close()
        user = dict(user)

        if user["info"] is not None:
            user["info"] = json.loads(user["info"])

        return AuthorizedUser.model_validate(dict(user))