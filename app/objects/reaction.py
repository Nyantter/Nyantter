from ..data import DataHandler
from .user import User
from pydantic import BaseModel
import asyncpg

class Reaction(BaseModel):
    id: int
    letter_id: int
    user_id: int
    reaction: str
    reaction_data: dict
