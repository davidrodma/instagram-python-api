# app/models/proxy.py
from app.common.types.id import ID
# app/models/proxy.py
from datetime import datetime

class Proxy:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.url:str = data.get('url')
        self.type:str = data.get('type')
        self.noteError:str = data.get('noteError')
        self.countErrors:int = data.get('countErrors')
        self.countFewMinutes:int = data.get('countFewMinutes')
        self.countSuccess:int = data.get('countSuccess')
        self.fewMinutesAt:datetime = data.get('fewMinutesAt') if data.get('fewMinutesAt') else None
        self.buyId:str = data.get('buyId')
        self.buyExpirationAt: datetime = data.get('buyExpirationAt') if data.get('buyExpirationAt') else None
        self.buyPeriod:int = data.get('buyPeriod') 
        self.createdAt:datetime = data.get('createdAt')
        self.status:int = data.get('status')
        self.change:bool = data.get('change') if data.get('change') else False
        self.countChange:int = data.get('countChange')
        self.countryCode:datetime = data.get('countryCode')
      

        


