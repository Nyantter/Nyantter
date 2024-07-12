from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime

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
    public_key: str