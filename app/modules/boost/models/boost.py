# app/models/boost.py
from app.common.types.id import ID
# app/models/boost.py
from datetime import datetime

class Boost:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.username:str = data.get('username')
        self.password:str = data.get('password')
        self.socialId:str = data.get('socialId')
        self.accountId:str = data.get('accountId')
        self.proxy:str = data.get('proxy')
        self.boostId:str = data.get('boostId')
        self.noteErrorBefore:str = data.get('noteErrorBefore')
        self.noteError:str = data.get('noteError')
        self.countChallenge:int = data.get('countChallenge')
        self.countBlocked:int = data.get('countBlocked')
        self.countUnblocked:int = data.get('countUnblocked')
        self.countCurrentFollower:int = data.get('countCurrentFollower')
        self.countCurrentLike:int = data.get('countCurrentLike')
        self.countCurrentComment:int = data.get('countCurrentComment')
        self.countCurrentStory:int = data.get('countCurrentStory')
        self.countUsed:int = data.get('countUsed')
        self.countError:int = data.get('countError')
        self.countSuccess:int = data.get('countSuccess')
        self.countFewMinutes:int = data.get('countFewMinutes')
        self.fewMinutesAt:datetime = data.get('fewMinutesAt') if data.get('fewMinutesAt') else None
        self.disabledAt:datetime = data.get('disabledAt') if data.get('disabledAt') else None
        self.expireAt:datetime = data.get('expireAt') if data.get('expireAt') else None
        self.pausedAtFollower:datetime = data.get('pausedAtFollower') if data.get('pausedAtFollower') else None
        self.pausedAtLike:datetime = data.get('pausedAtLike') if data.get('pausedAtLike') else None
        self.pausedAtComment:datetime = data.get('pausedAtComment') if data.get('pausedAtComment') else None
        self.pausedAtStory:datetime = data.get('pausedAtStory') if data.get('pausedAtStory') else None
        self.countryCode:str = data.get('countryCode')
        self.recoveredType:str = data.get('recoveredType')
        self.createdAt:datetime = data.get('createdAt')
        self.status:int = data.get('status')
        


