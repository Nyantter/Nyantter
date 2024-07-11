from pydantic import BaseModel

class Emoji(BaseModel):
    id: int
    image_url: str