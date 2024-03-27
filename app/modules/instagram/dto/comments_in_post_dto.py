from pydantic import BaseModel
from typing import List,Union

class CommentsInPostDto(BaseModel):
    pk:str = ''
    media_id:str = ''
    url:str = ''
    ids_action: str = ''
    usernames_action: str = ''
    max:int = 500