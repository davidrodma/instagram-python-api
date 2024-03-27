# app/models/item.py
from pydantic import BaseModel
from typing import List,Union

class IdsDto(BaseModel):    
    ids:Union[List[str], str]


class IdDto(BaseModel):    
    ids:str