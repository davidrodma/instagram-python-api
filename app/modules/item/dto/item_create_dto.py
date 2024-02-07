# app/models/item.py
from datetime import datetime
from typing import  Optional
from pydantic import BaseModel

class ItemCreateDto(BaseModel):
    name: str
    description: Optional[str] = ''
    create_at: Optional[datetime] = datetime.utcnow()
    status: int = 1