# app/models/config.py
from datetime import datetime
from typing import  Optional
from pydantic import BaseModel

class ConfigCreateDto(BaseModel):
    name: str
    title: str
    description: str
    type: str
    value: Optional[str] = ''
    jsonOptions: Optional[str] = ''
    classAdd: Optional[str] = ''
    createdAt: datetime = datetime.utcnow()
    status: int = 1
