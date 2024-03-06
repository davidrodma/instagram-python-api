# app/models/worker.py
from app.common.types.id import ID
# app/models/worker.py
from datetime import datetime

class Worker:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.username:str = data.get('username')
        self.password:str = data.get('password')
        self.proxy:str = data.get('proxy')
        self.proxyCreate:str = data.get('proxyCreate')
        self.typeProxy:str = data.get('typeProxy')
        self.countryProxy:str = data.get('countryProxy')
        self.workerId:str = data.get('workerId')
        self.groupType:str = data.get('groupType')
        self.provider:str = data.get('provider')
        self.price:float = data.get('price')
        self.costSms:float = data.get('costSms')
        self.info:str = data.get('info')
        self.noteErrorBefore:str = data.get('noteErrorBefore')
        self.noteError:str = data.get('noteError')
        self.countChallenge:int = data.get('countChallenge')
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
        self.nationality:str = data.get('nationality')
        self.recoveredType:str = data.get('recoveredType')
        self.createdAt:datetime = data.get('createdAt')
        self.status:int = data.get('status')
        


