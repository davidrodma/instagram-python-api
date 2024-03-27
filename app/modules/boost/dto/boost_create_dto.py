# app/models/boost.py
from datetime import datetime,timezone
from pydantic import BaseModel

class BoostCreateDto(BaseModel):
    username: str
    password: str
    accountId: str
    socialId: str = ''
    proxy:str = ''
    createdAt: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    status: int = 1
    noteErrorBefore:str = ""
    noteError:str = ""
    countChallenge: int = 0
    countCurrentFollower: int = 0
    countCurrentLike: int = 0
    countCurrentComment: int = 0
    countCurrentStory: int = 0
    countUsed: int = 0
    countError: int = 0
    countSuccess: int = 0
    countFewMinutes: int = 0
    countBlocked: int = 0
    countUnblocked: int = 0
    recoverChallenge: str = ""
    fewMinutesAt: datetime = None
    disabledAt: datetime = None
    expireAt: datetime = None
    pausedAtFollower: datetime = None
    pausedAtLike: datetime = None
    pausedAtComment: datetime = None
    pausedAtStory: datetime = None
    countryCode:str = "BR"
    recoverChallenge:str = ""