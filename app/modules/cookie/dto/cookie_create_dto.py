from app.common.models.model import Model
from datetime import datetime
from typing import  Optional
from pydantic import BaseModel

class CookieCreateDto(Model):
    username: str
    pk: Optional[str] = ''
    state: str
    createdAt: Optional[datetime] = datetime.utcnow()
    updatedAt: Optional[datetime] = None