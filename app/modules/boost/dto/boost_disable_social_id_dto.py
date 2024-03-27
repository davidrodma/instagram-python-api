from pydantic import BaseModel

class BoostDisableSocialIdDto(BaseModel):
    socialId: str
    reason: str = None