from datetime import datetime,timezone
from typing import  Optional
from pydantic import BaseModel, validator
from app.modules.config.services.config_service import ConfigService

class WorkerCreateDto(BaseModel):
    username: str
    password: str
    proxy:str = ''
    proxyCreate:str = ''
    typeProxy:str = ''
    countryProxy:str = ''
    provider: Optional[str] = ''
    createdAt: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    status: int = 1
    groupType:str = ""
    provider:str = ""
    price:float = None
    costSms:float = None
    info:str = ""
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
    recoverChallenge: str = ""
    fewMinutesAt: datetime = None
    disabledAt: datetime = None
    expireAt: datetime = None
    pausedAtFollower: datetime = None
    pausedAtLike: datetime = None
    pausedAtComment: datetime = None
    pausedAtStory: datetime = None
    nationality:str = ""
    recoverChallenge:str = ""
    isCreate:bool = False
    
    @validator('isCreate', pre=True, always=True)
    def transform_value(cls, isCreate, values, **kwargs):
        if isCreate:
            typeProxy = ConfigService.get_config_value('which-proxy-type-to-use-after-create-worker')
            if typeProxy and values.get('status'):
                 values['typeProxy'] = typeProxy
        return isCreate
  
    @validator('isCreate', pre=False, always=True)
    def remove_is_create(cls, v, values, **kwargs):
        return None