from pydantic import BaseModel
from typing import List,Union

class LikersInPostByIdDto(BaseModel):
    pk:str = ''
    media_id:str = ''
    ids_likers_action: List[Union[str, int]] | str | int