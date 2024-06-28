from pydantic import BaseModel

class Role(BaseModel):
    id: int
    image_url: str