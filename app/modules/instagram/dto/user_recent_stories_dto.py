from pydantic import BaseModel

class UserRecentStoriesDto(BaseModel):
    username:str
    pk:str = ''
    media_id:str = ''
    max:int = 20