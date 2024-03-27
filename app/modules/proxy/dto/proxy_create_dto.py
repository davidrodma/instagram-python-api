from datetime import datetime,timezone
from pydantic import BaseModel

class ProxyCreateDto(BaseModel):
    url:str
    type:str
    noteError:str = ""
    countErrors:int = 0
    countFewMinutes:int = 0
    countSuccess:int = 0
    fewMinutesAt:datetime = None
    buyId:str = ""
    buyExpirationAt: datetime = None
    buyPeriod:int = 0
    createdAt: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    status:int = 1
    change:bool = False
    countChange:int = 0
    countryCode:datetime = ""