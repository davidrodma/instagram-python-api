# app/models/item.py
from pydantic import BaseModel
from typing import List,Union

class StatusDto(BaseModel):    
    ids:Union[List[str], str]
    status:int