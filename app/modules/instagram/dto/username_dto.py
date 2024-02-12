from pydantic import BaseModel

class UsernameDto(BaseModel):
    username: str