from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    created_at: str
    handle: str
    display_name: Optional[str] = None
    icon_url: Optional[str] = None
    header_url: Optional[str] = None
    description: Optional[str] = None
    info: Optional[dict] = None