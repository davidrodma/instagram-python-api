from pydantic import BaseModel

class SaveBoostDto(BaseModel):
    username:str
    password:str
    accountId:str
    socialId:str
    proxy:str="random",
    status:int=1
    countryCode:str=""