# app/models/item.py
from datetime import datetime
from typing import  Optional
from app.common.types.model import Model
from pydantic import Field


class Item(Model):
    name: str
    description: Optional[str] = ''
    create_at: Optional[datetime] = datetime.utcnow()
    status: int = 1


    