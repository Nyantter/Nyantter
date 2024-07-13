import asyncpg
from pydantic import BaseModel

from ..data import DataHandler
from .User import User


class Reaction(BaseModel):
    id: int
    letter_id: int
    user_id: int
    reaction: str
    reaction_data: dict
