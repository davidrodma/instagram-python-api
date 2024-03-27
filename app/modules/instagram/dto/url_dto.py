from pydantic import BaseModel

class UrlDto(BaseModel):
    url: str