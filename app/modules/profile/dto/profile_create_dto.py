# app/models/profile.py
from datetime import datetime,timezone
from typing import  Optional
from pydantic import BaseModel

class ProfileCreateDto(BaseModel):
    username: str
    password: str
    provider: Optional[str] = ''
    createdAt: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    status: int = 1
    groupType:str = ""
    noteErrorBefore:str = ""
    noteError:str = ""
    countChallenge: int = 0
    countCurrent: int = 0
    countCurrentFollower: int = 0
    countCurrentLike: int = 0
    countCurrentComment: int = 0
    countCurrentStory: int = 0
    countUsed: int = 0
    countError: int = 0
    countSuccess: int = 0
    countFewMinutes: int = 0
    recoverChallenge: str = ""
