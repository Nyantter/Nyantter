from ..data import DataHandler
from .reaction import Reaction
from .user import User

from pydantic import BaseModel
from typing import Optional
import asyncpg

from datetime import datetime

class Letter(BaseModel):
    id: int
    user_id: int
    user: User
    created_at: datetime
    content: Optional[str] = None
    replyed_to: Optional[int] = None
    relettered_to: Optional[int] = None
    attachments: Optional[dict] = None
    reactions: list[Reaction] = []
