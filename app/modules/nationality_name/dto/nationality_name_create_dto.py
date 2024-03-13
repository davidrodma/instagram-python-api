# app/models/nationality_name.py
from datetime import datetime
from typing import  Optional
from pydantic import BaseModel

class NationalityNameCreateDto(BaseModel):
    romanName: str
    nativeName: str = ''
    gender: str = ''
    nationality: str
    type: str
    createdAt: datetime = datetime.utcnow()
    status: int = 1