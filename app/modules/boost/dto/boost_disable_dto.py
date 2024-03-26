from pydantic import BaseModel

class BoostDisableDto(BaseModel):
    username: str
    reason: str = ''