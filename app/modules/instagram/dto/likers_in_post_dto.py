from pydantic import BaseModel
from typing import List,Union

class LikersInPostDto(BaseModel):
    url:str
    usernames_action: List[str] | str